"""
Automatorより実行されるコマンドの修正

*** befor ***
import subprocess as sb
import os
sb.call("/usr/local/bin/python3 ~/Desktop/FinderPlus_2.app/Contents/FinderPlus_2.py",shell=True)
*** ***

*** after *** (Python管理ツールの変更に伴い、コマンドの変更)
import subprocess as sb
import os
sb.call("~/.pyenv/shims/python3 ~/Desktop/FinderPlus_2.app/Contents/FinderPlus_2.py", shell=True)
"""

"""
ディレクトリ"~"を正式なパスに変更
"""

#<Motion>だとメモリリークを起こすので、<Double-Button-1>等に変更
#current_dirはchdirで移動した後にgetcwdで取得
#内部フォルダの表示・非表示を関数化
#内部ディレクトリへの移動完了
#表示されるディレクトリは一つだけに制限完了
#表示された内部フォルダをクリックしても、さらに内部フォルダが開かれるバグを修正済み
#内包フォルダ表示時に位置がずれるバグ修正
#円のDragによってその円から出る線に対しては同時に移動できるように修正
#確定されたunder_directryをそれぞれが保持するように修正(必要かどうかは要判断)
#内部ディレクトリの展開方向をマウスに合わせるよう修正
#複数の内部ディレクトリを表示可能に修正
#連続クリックによるclick地の値の修正完了
#mvコマンド完成（Finderで確認済み）
"""
#マウスの移動によって線も動き、内包ディレクトリの確定方向を決めることがまだ実装できていない
#Drag&Dropの修正着手
#Drag&Dropによってovalが移動することは修正したが、oval間のlineがovalとつながりを持っていないため、lineがovalとともに動かないバグ
#line配列がovalないのマウスとともに動く線なのか、円と円を繋ぐ線なのかの区別ができていないバグ
#windowをscrollbarによってscrollできるようにする可能性あり
#例えば、ホームフォルダをDragした時に、その下にどんなディレクトリが確定されているのかの情報を与える必要がある
"""
#!!!!!pressは大域変数で、Motion時に宣言時の値が上書きされるので注意!!!!!

#mvコマンドで移動した後に移動先の内部フォルダに表示できていない
#mv=OFFにおいて、右クリックで円は消えてもdcd_under_dirが消えない
#delete_dcd_under_dirにおいて、inを使うとリスト[i]の一部分と一致しただけでtrueになってしまうので==を使う


"""
<関数一覧>
＊test
＊move_line
・which_left_click 		:マウスイベント<ButtonRelease-1>に対して関数分岐
・which_right_click		:マウスイベント<ButtonRelease-2>に対して関数分岐
・selection        		:フォルダの新規作成window表示中にmain_windowのディレクトリをクリックして、新規作成場所を指定
・hide_delete      		:確定されたディレクトリを右クリックで、自分自身及び確定下位ディレクトリ非表示!!!!!!!!!!!!!!!!!!!!!!!未完成!!!!!!!!!!!!!!!!!!
・drag_start       		:Dragし始め時に、ovalの位置とマウスの位置のずれを計算(実質クリック)
・dragging         		:Drag中の動作
・dist             		:マウスの位置とoval[i]との距離を算出し、最も近いoval[i]との距離を返す
・mv_command       		:mv_command実行
・search_dir       		:与えられたcurdirに対してupdirとindirを返す
・move_inner       		:右クリックされたら洗濯した内部ディレクトリに移動
・hide_curdir      		:右クリックされたら表示中の内部ディレクトリを非表示(move_innerの時に使われる)=非確定内部フォルダを右クリックしたら、右クリックされたフォルダと同じ親ディレクトリを持つ非確定フォルダ(内包フォルダ)を消す
・show_or_hide     		:クリックで、内包フォルダを表示するのか隠すのか、関数分岐
・show_inner       		:内包フォルダ表示
＊hide_dir
・hide_inner        		:選択されたディレクトリを親に持つ非確定ディレクトリを非表示(主に、Dragされた時にそのディレクトリの下位ディレクトリである内包フォルダを非表示に)
・click             		:mvコマンドON/OFFボタンの値確認
・sub_win_new_folder		:新規作成ボタンが押されたら、作成場所を指定するwindowを表示
・search            		:検索
・rollback          		:新規作成場所を選択するwindow表示中に目立たせるためのハイライトを元に戻す
・create_new_folder 		:新規作成ウィンドウを削除
・redraw            		:
・
"""

 # -*- coding: shift_jis -*

from tkinter import *
import os as os
from math import *
from sys import *
from time import *
import subprocess as subprocess
import tkinter.messagebox as m
import re
import traceback
import shutil as sh
from tkinter import ttk
from tkinter.colorchooser import *
from tkinter.filedialog import *


class Dirction_oval:
	def __init__(self, x, y, r, id):
		self.x = x
		self.y = y
		self.folder_direction_id = canvas.create_oval(x-r, y-r, x+r, y+r, tags="aaa")
		# self.dir_name =

		# canvas.tag_bind()


class Line_betOval:
	def __init__(self, st_x, st_y, end_x, end_y, oval_path):
		self.st_x, self.st_y, self.end_x, self.end_y = st_x, st_y, end_x, end_y
		self.oval_path   = oval_path
		self.color = self.get_color()
		# print(self.color)
		l=10
		th=90
		length = hypot(end_x-st_x, end_y-st_y)
		X = (end_x-st_x)*l/length+st_x
		Y = (end_y-st_y)*l/length+st_y
		x1 = (X-st_x)*cos(-th)-(Y-st_y)*sin(-th)+st_x
		y1 = (X-st_x)*sin(-th)+(Y-st_y)*cos(-th)+st_y
		x2 = (X-st_x)*cos(th)-(Y-st_y)*sin(th)+st_x
		y2 = (X-st_x)*sin(th)+(Y-st_y)*cos(th)+st_y
		self.line_bet_id2 = canvas.create_polygon(end_x, end_y, x1, y1, x2, y2, fill=self.color,tags="lineId_"+str(self.oval_path))


	def line(self, st_x, st_y, end_x, end_y, theta):
		return (end_x-st_x)*cos(radians(theta)) - (end_y-st_y)*sin(radians(theta))+st_x, (end_x-st_x)*sin(radians(theta)) + (end_y-st_y)*cos(radians(theta))+st_y


	def get_color(self):
		if self.oval_path.count("/") - home_dir.count("/") == 1:
			for i in range(len(line_color_and_path_list)):
				if line_color_and_path_list[i][0] == self.oval_path.lstrip(str(home_dir)):
					# print("***")
					return line_color_and_path_list[i][1]
		else:
			for i in range(len(line_color_and_path_list)):
				if self.oval_path.lstrip(str(home_dir)).split("/",1)[0] == line_color_and_path_list[i][0]:
					return line_color_and_path_list[i][1]



class Oval:
	def __init__(self, x, y, txt, current_dir_path, decide, fill_color, edge_color, txt_color):
		self.x, self.y         	= x, y
		self.curdir 			= current_dir_path
		self.updir, self.indir 	= self.search_dir(current_dir_path)
		self.fill_color = fill_color if os.path.isdir(current_dir_path) else "#ffffff"
		self.edge_color = edge_color
		self.txt_color = txt_color

		if os.path.isdir(current_dir_path):
			self.oval_id 		= canvas.create_polygon(x-folder_width/2, y-folder_height/2-folder_height/7, x-folder_width/2+folder_width*7/22, y-folder_height/2-folder_height/7, x-folder_width/2+folder_height/2, y-folder_height/2, x-folder_width/2+folder_width, y-folder_height/2, x-folder_width/2+folder_width, y-folder_height/2+folder_height-folder_height/7, x-folder_width/2, y-folder_height/2+folder_height-folder_height/7, width=1, fill=self.fill_color, outline=self.edge_color, tags="id_"+str(current_dir_path))
			self.oval_id2		= canvas.create_polygon(x-folder_width/2, y-folder_height/2, x-folder_width/2+folder_width, y-folder_height/2, x-folder_width/2+folder_width, y-folder_height/2+folder_height, x-folder_width/2, y-folder_height/2+folder_height, width=1, fill=self.fill_color, outline=self.edge_color, tags="id_"+str(current_dir_path))
		elif os.path.isfile(current_dir_path):
			# print("+++++")
			self.oval_id 		= canvas.create_polygon(x-file_width/2, y-file_height/2, x-file_width/2+file_width*5/9, y-file_height/2, x+file_width/2, y-file_height/2+file_width*5/9, x+file_width/2, y+file_height/2, x-file_width/2, y+file_height/2, width=1, fill=self.fill_color, outline=self.edge_color, tags="id_"+str(current_dir_path))
		else:
			print("Not File or Dir")
			pass
			# quit()
		self.txt               = txt
		#ファイル名が長い場合に対処する必要あり
		# self.txt_id            = canvas.create_text(x+r_oval, y+r_oval, text=txt)
		self.txt_id = canvas.create_text(x, y+folder_height/2+8, text=txt, tags="id_"+str(current_dir_path),fill=self.txt_color) if len(self.txt) < 8 else canvas.create_text(x, y+folder_height/2+17, text=txt[0:7]+"\n"+txt[7:14], tags="id_"+str(current_dir_path),fill=txt_color)
		self.click             = False		#内包フォルダが表示されているかどうか
		self.decision          = decide	#確定されたディレクトリであるかどうか
		# 下位ディレクトリのうち確定されているディレクトリを保持(oval_id)*********これはded_under_dirで代用されてる？
		# self.under_dir       = list()
		# 各ovalが何本の線でつながっているのか記憶
		self.connect_line      = list()
		# 各ovalに対して、そのディレクトリ下の確定されたディレクトリを格納
		self.dcd_under_dir     = list()
		# self.speed_x,self.seppd_y=self.calc_speed()



		# print(self.curdir)
		#クリックされたらないフォルダを表示・非表示
		canvas.tag_bind("id_"+str(self.curdir), "<ButtonRelease-1>", self.which_left_click)
		# canvas.tag_bind(self.txt_id, "<ButtonRelease-1>", self.which_left_click)
		canvas.tag_bind("id_"+str(self.curdir), "<Double-Button-1>", self.open)
		# canvas.tag_bind(self.txt_id, "<Double-Button-1>", self.open)
		#***クリックされたらディレクトリ移動
		canvas.tag_bind("id_"+str(self.curdir), "<ButtonRelease-2>", self.which_right_click)
		# canvas.tag_bind(self.txt_id,"<ButtonRelease-2>", self.which_right_click)
		#ドラッグされたらディレクトリ移動
		canvas.tag_bind("id_"+str(self.curdir), "<1>", self.drag_start)
		# canvas.tag_bind(self.txt_id, "<1>", self.drag_start)

		canvas.tag_bind("id_"+str(self.curdir), "<Button1-Motion>", self.dragging)
		canvas.bind("<Motion>", self.draw_or_hide_direction_oval)
		# canvas.tag_bind("aaa", "<ButtonRelease-2>", self.abc)




	def direction_point(self,event,num,dist):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		if len(line)>1:
			canvas.delete("bbb")
			del(line[1])
		else:
			line.insert(0,Line(oval[num].x, oval[num].y, oval[num].x+(event.x-oval[num].x)*r_folder_direction/dist, oval[num].y+(event.y-oval[num].y)*r_folder_direction/dist))

	def draw_or_hide_direction_oval(self, event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		# print(direction_oval_num)
		global direction_oval_num

		dist,num=-1,-1
		for i in range(len(oval)):
			if oval[i].decision == False:
				if sqrt(pow(event.x-oval[i].x,2)+pow(event.y-oval[i].y,2))<r_folder_direction:
					dist,num=sqrt(pow(event.x-oval[i].x,2)+pow(event.y-oval[i].y,2)), i
					break

		# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		# ここのovalリストが out of range するバグ
		# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		try:
			if sqrt(pow(oval[direction_oval_num-1].x,2)+pow(oval[direction_oval_num-1].y,2))>dist:
					oval[direction_oval_num].hide_direction_oval(event)
					direction_oval_num=num
		except:
			pass
		if dist>=0:
			if len(direction_oval)>0:
				# print("AAA")
				return
			else:
				# print("BBB")
				oval[num].draw_direction_oval(event,num,dist)
			# if dist>0:
			# 	self.direction_point(event,num,dist)
		else:
			if len(direction_oval)>0:
				# print("CCC")
				oval[num].hide_direction_oval(event)
			else:
				# print("DDD")
				return

	def draw_direction_oval(self,event,num,dist):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		# if len(direction_oval)>0:
			# return
		direction_oval.append(Dirction_oval(self.x, self.y,r_folder_direction,oval[num].curdir))
		if dist>0:
			line.insert(0,Line(oval[num].x, oval[num].y, oval[num].x+(event.x-oval[num].x)*r_folder_direction/dist, oval[num].y+(event.y-oval[num].y)*r_folder_direction/dist,str(self.curdir)))

	def hide_direction_oval(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		canvas.delete("aaa")
		del(direction_oval[:])
		canvas.delete("bbb")
		del(direction_oval[:])

	def calc_speed():
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		pass


	def which3(self, event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		if enter_oval == True:
			return
		self.move_line(event)

	def which4(self, event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		if enter_oval == True:
			pass



	def test(self, event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		pass

	def move_line(self, event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		# global inline
		# if inline==True:
		#"""
		dist = sqrt(pow(self.x-event.x, 2) + pow(self.y-event.y, 2))
		line.insert(0,Line(self.x, self.y, self.x+(event.x-self.x)*folder_width/2/dist, self.y+(event.y-self.y)*folder_height/2/dist))
		if len(line)>1:
			canvas.delete(line[1].id)
			del line[1]
			# print(len(line))
		#"""
		"""
		theta = atan2(event.y-self.y-r_oval, event.x-self.x-r_oval)
		"""



	def open(self, event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		if os.path.isfile(self.curdir):
			subprocess.call("open %s"%re.sub(r'[)]',"\)",re.sub(r'[(]',"\(",re.sub(r'[\s]',"\ ",str(self.curdir)))), shell=True)
		else:
			return

	#マウスイベント<ButtonRelease-1>に対して、dragされていた場合はmv_commandを実行し、
	#dragされていなかった場合にはshow_or_hideを実行
	def which_left_click(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global drag,new_folder_button
		global move_x, move_y
		# print("Function : which_left_click")

		# ***本当はこの部分で内部フォルダの移動を書きたい
		"""
		global showing_indir

		# showing_indir = not showing_indir
		print("showing_indir : " + str(showing_indir))
		print("self.decisoin : " + str(self.decision))
		if self.decision==True:
			print("AAA")
			# print(drag)
			if showing_indir == False:
				self.hide_delete()
		else:
			print("BBB")
			# print(drag)
			self.move_inner(event)
			showing_indir = False
		# ***
		"""
		#新規作成ボタンが押されている時
		if new_folder_button==True:
			#新規作成windowが非表示になったら
			if sub_win.winfo_exists()==False:
				rollback()
			else:
				self.selection()
				if searching == True:
					search()
		#ドラッグされた後マウスが離されたらmv_command実行
		elif drag==True and var.get()==0:# and self.dist(event)[1]>0:	#len(redraw_list)>0
			self.redraw()
		elif drag==True and var.get()==1:
			self.mv_command(event)
		#それ以外の時は単なるクリックによってマウスから離された
		elif drag==False:
			self.show_or_hide()
		drag=False
		move_x, move_y=(0,0)
		# concern_click_decision()
		# concern_dcd_under_dir()
		# concern_curdir()
		# concern_updir()
		# concern_file_dir()
		# print("CWD : "+os.getcwd())
		# concern_dir()
		# concern_redrawlist()
		# concern_drag()
		# concern_len()
		# concern_pos()

	def which_right_click(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global showing_indir
		# コメント解除必須
		# ***
		if self.decision==True:
			# print(drag)
			if showing_indir == False:
				self.hide_delete()
		else:
			# print(drag)
			self.move_inner(event)
			showing_indir = False
		# ***

		# concern_click_decision()
		# concern_dcd_under_dir()
		# concern_curdir()
		# concern_updir()
		# concern_dir()
		# concern_redrawlist()
		# concern_drag()
		# concern_len()
		# concern_pos()

	#新規作成window表示中にメインウィンドウの縁をクリックして、新規作成場所を指定
	def selection(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		for i in range(len(selected_oval)):
			canvas.delete(selected_oval[i])
		del selected_oval[:]
		selected_oval.append(canvas.create_oval(self.x-folder_width,self.y-folder_width,self.x+folder_width,self.y+folder_width,outline=None,fill="Yellow"))
		# for i in range(len(oval)):
		# 	canvas.itemconfigure("id_"+str(oval[i].curdir),fill=bg_color)
		# 	canvas.itemconfigure(oval[i].txt_id,fill=txt_color)
		# canvas.itemconfigure(self.oval_id,fill="Red")

		canvas.lower(selected_oval[0])
		buffer1.set("%s"%str(self.curdir))


	#確定された円(self.decision=True)を右クリックするとその円とその円の確定された下位ディレクトリの円を削除
	#同時にその円の確定された下位ディレクトリリスト(self.dcd_under_dir)を初期化
	def hide_delete(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		# print("Before delete dcd_under_dir :\n%s"%self.dcd_under_dir)
		if self.curdir == oval[0].curdir:
			return
		#円自体の削除
		delete_ovals=list()
		#dcd_under_dirの削除
		delete_dcd_under_dir=list()
		#line_bet_ovalの削除
		delete_line=list()
		#削除すべきdcd_under_dirの選定
		for i in range(len(oval)):
			if oval[i].curdir == self.curdir:
				# continue
				break
			for j in range(len(oval[i].dcd_under_dir)):
				if oval[i].dcd_under_dir[j] == self.curdir and delete_dcd_under_dir.count([i,j])==0:
					delete_dcd_under_dir.append([i,j])
				for k in range(len(self.dcd_under_dir)):
					#　消した円のdcd_under_dirを引き継ぐ
					if oval[i].dcd_under_dir[j] == self.dcd_under_dir[k] and delete_dcd_under_dir.count([i,j])==0:
						delete_dcd_under_dir.append([i,j])


		#delete_dcd_under_dirに正しく記録されているかの確認
		#print(delete_dcd_under_dir)
		"""
		for i in range(len(delete_dcd_under_dir)):
		# 	#このディレクトリの中の
			print(oval[delete_dcd_under_dir[i][0]].curdir)
		# 	#この確定回ディレクトリを削除する
			print("  -> "+str(oval[delete_dcd_under_dir[i][0]].dcd_under_dir[delete_dcd_under_dir[i][1]]))
		"""
		#削除すべき円の選定
		"""
		for i in range(len(delete_dcd_under_dir)):
			for j in range(len(oval)):
				if oval[delete_dcd_under_dir[i][0]].dcd_under_dir[delete_dcd_under_dir[i][1]]==oval[j].curdir:
					if delete.count(oval[j].curdir)==0:
						delete.append(j)
					# if delete.count(j)==0:
					# 	delete.append(j)
		"""
		for i in range(len(delete_dcd_under_dir)):
			if delete_ovals.count(oval[delete_dcd_under_dir[i][0]].dcd_under_dir[delete_dcd_under_dir[i][1]])==0:
				delete_ovals.append(oval[delete_dcd_under_dir[i][0]].dcd_under_dir[delete_dcd_under_dir[i][1]])
		# print(delete_ovals)
		# print("-----")
		# for i in range(len(delete)):
		# 	print(oval[delete[i]].curdir)
		# print("-----")

		"""
		ここからdebug
		"""

		#delete_dcd_under_dirに基づいて確定回ディレクトリを削除
		for i in reversed(range(len(delete_dcd_under_dir))):
			del(oval[delete_dcd_under_dir[i][0]].dcd_under_dir[delete_dcd_under_dir[i][1]])

		#deleteに基づいて円と線を削除
		"""
		for i in reversed(range(len(delete_ovals))):
			for j in reversed(range(len(line_betOval))):
				if oval[delete_ovals[i]].curdir == line_betOval[j].oval_path:
					canvas.delete(line_betOval[j].line_bet_id)
			canvas.delete(oval[delete[i]].oval_id)
			canvas.delete(oval[delete[i]].txt_id)
		"""
		for i in reversed(range(len(delete_ovals))):
			for j in range(len(oval)):
				if delete_ovals[i] == oval[j].curdir:
					for k in range(len(line_betOval)):
						if line_betOval[k].oval_path == oval[j].curdir and delete_line.count(k)==0:
							delete_line.append(k)
							# canvas.delete(line_betOval[k].line_bet_id)
							canvas.delete("lineId_"+line_betOval[k].oval_path)
					canvas.delete("id_"+str(oval[j].curdir))
					# canvas.delete(oval[j].txt_id)

		"""確認"""
		# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		# print(delete_line)
		# 上のfor文よりlistには大きい順に並んでいるので、以下のfor文ではそのままの順番でdeleteすれば良い
		for i in range(len(delete_line)):
			# print(line_betOval[delete_line[i]].oval_path)
			del(line_betOval[delete_line[i]])

		#ovalリストから記録を抹消
		"""
		for i in reversed(range(len(delete))):
			del(oval[delete[i]])
		"""
		# for i in reversed(range(len(delete_line))):
			# del(line_betOval[delete_line[i]])
		for i in reversed(range(len(delete_ovals))):
			for j in reversed(range(len(oval))):
				if delete_ovals[i] == oval[j].curdir:
					del(oval[j])

	#Dragし始め時に、ovalの位置とマウスの位置のずれを計算
	def drag_start(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global error_posx, error_posy
		global drag
		drag=False
		error_posx = event.x - self.x
		error_posy = event.y - self.y

	#ドラッグされた時に線と確定下位ディレクトリを一時的に非表示にする(ドラッグ終了後に再び表示するため、リストから削除はしない)
	def hide(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global redraw_list
		for i in range(len(oval)):
			for j in range(len(self.dcd_under_dir)):
				if self.dcd_under_dir[j] == oval[i].curdir:
					canvas.delete("id_"+str(oval[i].curdir))
					# canvas.delete(oval[i].txt_id)
					for k in range(len(line_betOval)):
						if oval[i].curdir == line_betOval[k].oval_path:
							# canvas.delete(line_betOval[k].line_bet_id)
							canvas.delete("lineId_"+line_betOval[k].oval_path)
							if redraw_list.count([i,k])==0:
								redraw_list.append([i,k])
							"""
							for l in range(len(redraw_list)):
								if redraw_list[l][0] == i:
									continue
								if l==len(redraw_list)-1:
									redraw_list.append([i,k])
							"""
								# break
					# break
		#redrawリストに重複データあり(最終的にappend時に重複データに対処する)del list[a:b]を使う
		# for i in range(len(redraw_list)):
		# 	for j in reversed(range(i+1,len(redraw_list))):
		# 		if redraw_list[i] == redraw_list[j]:
		# 			del(redraw_list[j])
		# for i in range(len(redraw_list)):
		# 	print(redraw_list[i])

		for i in range(len(redraw_list)):
			for j in reversed(range(i+1,len(redraw_list))):
				if redraw_list[i][0] == redraw_list[j][0]:
					del(redraw_list[j])

	def redraw(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global redraw_list
		global move_x, move_y
		drag=False

		# print("LEN = %d"%len(redraw_list))
		# print(redraw_list.count(redraw_list[0]))
		for i in reversed(range(len(redraw_list))):
			# print(oval[redraw_list[i][0]].curdir)		#ここでredraw_listが正しいことを確認
			#位置がおかしい！！！
			# 線も再度絵画
			line_betOval.append(Line_betOval(line_betOval[redraw_list[i][1]].st_x+move_x, line_betOval[redraw_list[i][1]].st_y+move_y, line_betOval[redraw_list[i][1]].end_x+move_x, line_betOval[redraw_list[i][1]].end_y+move_y, oval[redraw_list[i][0]].curdir))
			# canvas.tag_lower(line_betOval[-1].line_bet_id)
			canvas.tag_lower("lineId_"+line_betOval[-1].oval_path)
			oval.append(Oval(oval[redraw_list[i][0]].x+move_x, oval[redraw_list[i][0]].y+move_y, oval[redraw_list[i][0]].txt, oval[redraw_list[i][0]].curdir, True, fill_color, edge_color, txt_color))
			"""空白置換"""
			"""
			txt_rearange=re.sub(r'[\s]',"_",str(oval[redraw_list[i][0]].txt))
			path_rearange=re.sub(r'[\s]',"_",str(oval[redraw_list[i][0]].curdir))
			oval.append(Oval(oval[redraw_list[i][0]].x+move_x, oval[redraw_list[i][0]].y+move_y, txt_rearange, path_rearange, True, fill_color, edge_color, txt_color))
			"""
			oval[len(oval)-1].dcd_under_dir = oval[redraw_list[i][0]].dcd_under_dir

			del(oval[redraw_list[i][0]])
			del(line_betOval[redraw_list[i][1]])

		# print("\-------------------------------")
		del redraw_list[:]
		# print("LEN AFTER : %d"%len(redraw_list))
		move_x,move_y=(0,0)


	#Drag中は、drag_startで計算した誤差を考慮した上で、マウスとともに移動
	def dragging(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global drag
		global error_posx, error_posy
		global move_x, move_y
		# concern_redrawlist()
		# concern_dcd_under_dir()
		concern_drag()
		#内部フォルダ表示時にドラッグされたら内部フォルダを非表示にし、ドラッグされたフォルダはclickされていないことに
		if self.click==True:
			self.hide_inner()
			# concern_dcd_under_dir()
		if len(self.dcd_under_dir)>0:
			self.hide()
			# concern_dcd_under_dir()
		self.click=False

		#dragされている
		drag=True
		canvas.move("id_"+self.curdir, event.x-self.x-error_posx, event.y-self.y-error_posy)
		# canvas.move(self.txt_id, event.x-self.x-error_posx, event.y-self.y-error_posy)
		move_x += event.x-self.x-error_posx
		move_y += event.y-self.y-error_posy
		#selfのx,y座標を更新
		self.x = event.x - error_posx
		self.y = event.y - error_posy
		#線

			# if line_betOval[i].oval_path == self.curdir:
				# canvas.move(line_betOval[i].line_bet_id, event.x-self.x-error_posx, event.y-self.y-error_posy)
				# line_betOval[i].end_x += event.x-self.x-error_posx
				# line_betOval[i].end_y += event.y-self.y-error_posy
				# canvas.coords(line_betOval[i].line_bet_id,line_betOval[i].st_x,line_betOval[i].st_y,line_betOval[i].end_x,line_betOval[i].end_y)


		#Drag終了時に<ButtonRelease-1>によってshow_or_hide関数が実行されるのを阻止
		#（実質的にはhide_innerが実行されるようにしている）
		# self.click = True
		#mvボタンがONの時はmv_command実行
		# if var.get()==1:
			# self.mv_command(event)

		#ドラッグされた円に合わせて線の長さ変更
		self.ch_line_len()
		# concern_dcd_under_dir()
		# concern_click_decision()

	def ch_line_len(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		n=None
		for i in range(len(oval)):
			if self.updir == oval[i].curdir:
				n=i
				# print("***")
				# concern_updir()
				# print(oval[i].curdir)
		if n==None:
			return
		for i in range(len(line_betOval)):
			if line_betOval[i].oval_path == self.curdir:
				theta = atan2(self.y-oval[n].y, self.x-oval[n].x)
				st_x = oval[n].x# + r_oval*cos(pi-theta)
				st_y = oval[n].y# + r_oval*sin(pi-theta)
				end_x = self.x# + r_bet_oval*cos(theta)
				end_y = self.y# + r_bet_oval*sin(theta)
				l=10
				th=90
				length = hypot(end_x-st_x, end_y-st_y)
				X = (end_x-st_x)*l/length+st_x
				Y = (end_y-st_y)*l/length+st_y
				x1 = (X-st_x)*cos(-th)-(Y-st_y)*sin(-th)+st_x
				y1 = (X-st_x)*sin(-th)+(Y-st_y)*cos(-th)+st_y
				x2 = (X-st_x)*cos(th)-(Y-st_y)*sin(th)+st_x
				y2 = (X-st_x)*sin(th)+(Y-st_y)*cos(th)+st_y
				# canvas.coords(line_betOval[i].line_bet_id,st_x,st_y,end_x,end_y)
				canvas.coords("lineId_"+str(line_betOval[i].oval_path),end_x,end_y,x1,y1,x2,y2)
				line_betOval[i].st_x, line_betOval[i].st_y = st_x, st_y
				line_betOval[i].end_x, line_betOval[i].end_y = end_x, end_y
				#線と円の重なり順を変える
				# canvas.tag_lower(line_betOval[i].line_bet_id)
				canvas.tag_lower("lineId_"+str(line_betOval[i].oval_path))

	#マウスの位置とoval[i]との距離算出し、最も近いoval[i]との距離を返す
	def dist(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		dist=max(w,h)
		num=-1
		for i in range(len(oval)):
			if self.curdir != oval[i].curdir:
				d=sqrt(pow(event.x-oval[i].x,2)+pow(event.y-oval[i].y,2))
				if dist>d:
					dist=d
					num=i
		# print(dist)
		return dist,num

	#mv_command実行
	"""修正前(~ 2016/11/24 16:55)
	def mv_command(self,event):
		# print("Function : mv_command")
		global drag
		# print(drag)
		#万が一mvこの関数(mv_command)実行中にmvボタンがOFFになったらmv_commandを終了し、drag関数に戻る
		if var.get()==0:
			self.dragging(event)
		#mv_command実行最終確認
		elif var.get()==1:
			dist,num=self.dist(event)
			if dist<r_oval and num>=0 and drag==True:
				#ドラッグされたディレクトリのキャンバス上の表示に関する削除
				canvas.delete(self.oval_id)
				canvas.delete(self.txt_id)
				for i in range(len(line_betOval)):
					if line_betOval[i].oval_path == self.curdir:
						canvas.delete(line_betOval[i].line_bet_id)
						break
				# print("lll")
				# print(self.txt)
				# print("*****Terminal*****")
				move_from=self.curdir
				move_to=oval[num].curdir
				# print(move_from)
				# print(move_to)
				subprocess.call("mv %s/ %s/"%(move_from,move_to),shell=True)
				#mvコマンド実行後にoval[i]のディレクトリ位置を修正

				#indir修正
				#これは必要なし？
				#dcd_under_dir修正(selfの上位確定ディレクトリに対して、ded_under_dirにあるselfを削除)
				for i in range(len(oval)):
					for j in range(len(oval[i].dcd_under_dir)):
						if oval[i].dcd_under_dir[j] == move_from:
							del(oval[i].dcd_under_dir[j])
							break
				#dcd_under_dir修正(mv移動先のcurdirを持つovalのdcd_under_dirにselfの新しいcurdirを追加)
				for i in range(len(oval)):
					if move_to in oval[i].dcd_under_dir:
						oval[i].dcd_under_dir.append(str(move_to)+"/"+self.txt)
				#dcd_under_dir修正(上でできなかったmove_toのdcd_under_dirにselfのcurdirを追加)
				for i in range(len(oval)):
					if oval[i].curdir == move_to:
						oval[i].dcd_under_dir.append(str(move_to)+"/"+self.txt)
				#curdirの修正
				self.curdir=str(move_to)+"/"+self.txt
				#updir修正
				self.updir=move_to
	"""
	def mv_command(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global drag,direction_oval_num
		global quick_path_list
		# print(drag)
		#万が一mvこの関数(mv_command)実行中にmvボタンがOFFになったらmv_commandを終了し、drag関数に戻る
		if var.get()==0:
			self.dragging(event)
		#mv_command実行最終確認
		elif var.get()==1:
			dist,num=self.dist(event)
			if dist<r_oval and num>=0 and drag==True:
				drag = False
				#selfの親ディレクトリのindirからselfを削除
				for i in range(len(oval)):
					if oval[i].curdir == self.updir:
						oval[i].indir.remove(str(self.curdir.rsplit("/",1)[1]))
				#移動先のディレクトリのindirに追加
				oval[num].indir.append(str(self.curdir.rsplit("/",1)[1]))

				"""
				for i in reversed(range(len(self.dcd_under_dir))):
					for j in reversed(range(len(oval))):
						if oval[j].curdir == self.dcd_under_dir[i]:
							oval[j].hide_delete()
				"""
				#フォルダの移動と同時にクイックアクセスバーに登録されていたらパスを変更
				for k in range(len(quick_path_list)):
					if quick_path_list[k] == self.curdir:
						quick_path_list[k]=str(str(oval[num].curdir)+"/"+str(self.curdir.rsplit("/",1)[1]))
				#Terminal上の移動
				sh.move(str(self.curdir), str(oval[num].curdir)+"/"+str(self.curdir.rsplit("/",1)[1]))
				#selfの削除
				self.hide_delete()
				# for i in range(len(oval)):
					# oval[i].refresh_dir()
			del redraw_list[:]
			direction_oval_num=-1
			del direction_oval[:]

	def refresh_dir(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		#indirリストの削除
		for i in range(len(self.indir)):
			self.indir.pop()
		# print(self.indir)

		#indirリストの再構成
		dammy, self.indir = self.search_dir(self.curdir)


#self.updir, self.indir = self.search_dir(current_dir_path)

	#カレントディレクトリ、上位・下位ディレクトリを調べる
	def search_dir(self, current_dir):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global hidden_f
		# print("B : "+str(os.getcwd()))
		# print(self.curdir)
		# print(current_dir)
		# try:
		# 	self.refresh_dir()
		# except:
		# 	print("定義されていません")
		inner_dir=list()
		if os.path.isdir(current_dir):
			os.chdir(current_dir)
			# print("C : "+str(os.getcwd()))
			#上位ディレクトリ
			os.chdir("..")
			upper_dir = os.getcwd()
			os.chdir(current_dir)
			#下位ディレクトリ
			# print(os.getcwd())
			# print(os.listdir())
			for file in os.listdir():
				# if os.path.isdir(file) and file[0]!="." and file[0]!="$":
				try:
					if hidden_f.get() == 0:
						if file[0]!="." and file[0]!="$":
							inner_dir.append(file)
					elif hidden_f.get() == 1:
						inner_dir.append(file)
				except:
					if file[0]!="." and file[0]!="$":
							inner_dir.append(file)
		else:
			# print("D : "+str(current_dir))
			upper_dir = str(current_dir).rsplit("/",1)[0]
		# print(self.curdir)
		# print("  - "+str(inner_dir))
		# print("A : "+str(os.getcwd()))
		return str(upper_dir), inner_dir

	#右クリックされた時に内部ディレクトリに移動
	def move_inner(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global drag
		drag=False
		#確定されたディレクトリを右クリックしても新たに内部ディレクトリに移動するのを防止
		#which_right_clickからmove_innerが実行される条件はdecision=Falseであるから、ここでdicision=Trueはおそらくありえないので不要？
		if self.decision==True:
			return
		#すでに開いている場合は何もしない
		for i in range(len(oval)):
			if self.curdir == oval[i].curdir and oval[i].decision == True:
				self.hide_curdir()
				# print(oval[i].txt)
				return

		mouseX, mouseY = event.x, event.y
		theta = atan2(mouseY-self.y, mouseX-self.x)	#弧度法（x軸からy軸正の向きに0~pi,x軸からy軸ふの向きに0~-pi）
		self.hide_curdir()
		"""螺旋状に配置する場合"""

		for i in range(len(oval)):
			if self.updir == oval[i].curdir:
				st_x, st_y = oval[i].x, oval[i].y
				end_x=st_x+r_bet_oval*cos(theta)
				end_y=st_y+r_bet_oval*sin(theta)

				# line_betOval.append(Line_betOval(p,q,p+(r_bet_oval)*cos(theta),q+(r_bet_oval)*sin(theta), self.curdir))
				line_betOval.append(Line_betOval(st_x,st_y,end_x,end_y, self.curdir))
				# canvas.tag_lower(line_betOval[-1].line_bet_id)
				canvas.tag_lower("lineId_"+line_betOval[-1].oval_path)

				# count=0
				# p=5
				# self.move(p)
				# for i in range(20):
					# end_x, end_y = st_x+(end_x-st_x)*self.easeInOutQuint(i,0,1,4), st_y+(end_y-st_y)*self.easeInOutQuint(i,0,1,4)
					# canvas.coords(line_betOval[len(line_betOval)-1], st_x, st_y, end_x, end_y)
				# self.easeInOutQuint(0,0,1,4, p,q,p+(r_bet_oval)*cos(theta),q+(r_bet_oval)*sin(theta),0)
				# self.easeInOutQuint(0,0,1,4, p,q,p+(100)*cos(theta),q+(100)*sin(theta),0)
				oval.append(Oval(end_x,end_y,self.txt,self.curdir, True, fill_color, edge_color,txt_color))
				# line_betOval.append(Line_betOval(p,q,p+(r_bet_oval-2*r_oval)*cos(theta),q+(r_bet_oval-2*r_oval)*sin(theta), self.curdir))

				# print("\nLINE %s"%self.curdir)
				break

		#下位ディレクトリの保存
		# for i in range(len(oval)):
		# 	if self.updir == oval[i].curdir:
		# 		oval[i].under_dir.append(self.oval_id)

		#各確定ディレクトリに対して確定された下位ディレクトリを保存
		path = str(self.curdir)
		depth =str(self.curdir).count("/")-2
		for i in range(depth):
			for j in range(len(oval)):
				if path.rsplit("/",1)[0] == oval[j].curdir:
					oval[j].dcd_under_dir.append(self.curdir)
					break
			path = path.rsplit("/",1)[0]

		# concern_click_decision()

	def move(self,p):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		# canvas.coords(line_betOval[len(line_betOval)-1].line_bet_id,canvas.bbox(line_betOval[len(line_betOval)-1].line_bet_id)[0],canvas.bbox(line_betOval[len(line_betOval)-1].line_bet_id)[1],canvas.bbox(line_betOval[len(line_betOval)-1].line_bet_id)[2]+p,canvas.bbox(line_betOval[len(line_betOval)-1].line_bet_id)[3]+p)
		canvas.coords("lineId_"+line_betOval[len(line_betOval)-1].oval_path,canvas.bbox("lineId_"+line_betOval[len(line_betOval)-1].oval_path)[0],canvas.bbox("lineId_"+line_betOval[len(line_betOval)-1].oval_path)[1],canvas.bbox("lineId_"+line_betOval[len(line_betOval)-1].oval_path)[2]+p,canvas.bbox("lineId_"+line_betOval[len(line_betOval)-1].oval_path)[3]+p)
		if end_x-canvas.bbox(self.curdir)[2]<=0 and end_y-canvas.bbox(self.curdir)[3]<=0:
			return
		else:
			root.after(1000,self.move(p))

	def easeInOutQuint(self, t, b, c, d):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		t /= d/2
		if t < 1:
			return c/2*t*t*t*t*t + b
		t -= 2
		return c/2*(t*t*t*t*t + 2) + b
	"""
	def easeInOutQuint(self, t, b, c, d, st_x,st_y,end_x, end_y,count):
		# print(t)
		t /= d/2
		if t < 1:
			# pass
			print(c/2*t*t*t*t*t + b)
			canvas.coords(line_betOval[len(line_betOval)-1].line_bet_id,st_x,st_y,st_x+(end_x-st_x)*(c/2*t*t*t*t*t + b),st_y+(end_y-st_y)*(c/2*t*t*t*t*t + b))
			# return c/2*t*t*t*t*t + b
			count+=1
			canvas.after(500,self.easeInOutQuint(count,b,c,d,st_x,st_y,end_x,end_y,count))
		else:
			t -= 2
			print(c/2*(t*t*t*t*t + 2) + b)
			canvas.coords(line_betOval[len(line_betOval)-1].line_bet_id,st_x,st_y,st_x+(end_x-st_x)*c/2*(t*t*t*t*t + 2) + b,st_y+(end_y-st_y)*(c/2*(t*t*t*t*t + 2) + b))
		# return c/2*(t*t*t*t*t + 2) + b
			count+=1
			if count<5:
				canvas.after(500,self.easeInOutQuint(count,b,c,d,st_x,st_y,end_x,end_y,count))
			else:
				return
	"""

	#右クリックした時に同ディレクトリ内のファイルを非表示
	def hide_curdir(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		delete_current=list()
		for i in range(len(oval)):
			if self.updir == oval[i].updir and self.decision == False and oval[i].decision == False:
				canvas.delete("id_"+str(oval[i].curdir))
				# canvas.delete(oval[i].oval_id)
				delete_current.append(i)
		for i in delete_current:
			del oval[delete_current[0]]
		#ホームフォルダ以外が選択された時に、ホームフォルダのclick判定をFalseに
		if self.curdir != oval[0].curdir:
			oval[0].click = False
		#内包フォルダが確定されてたのファイルが非表示になった時に、親ディレクトリのclick判定をFalseに
		for i in range(len(oval)):
			if oval[i].curdir == self.updir:
				oval[i].click = False



	def show_or_hide(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)

		# print("__________________________\n" + str(self.curdir))
		# for i in range(len(oval)):
		# 	print("  " + str(i) + "\t" + str(oval[i].updir) + "\t\t" + str(oval[i].decision) + "\t\t" + "%-40s"%str(oval[i].curdir) + "\t" + str((str(oval[i].updir)==str(self.curdir))))
		# print("--------------------------")

		# print("Before")
		# concern_click_decision()
		#連続クリックに対してself以外のclickをFalseにし、表示されている内部フォルダの親元のclickはtrueのまま変化させない
		for i in range(len(oval)):
			if self.curdir == oval[i].curdir or (self.updir == oval[i].curdir and self.decision == False):
				pass
			else:
				oval[i].click = False

		if not self.click:
			if os.path.isdir(self.curdir):
				self.file_read()
			self.show_inner()
		else:
			self.hide_inner()
		#表示された内包フォルダをクリックしても何も起こらないようにする(clickの値の変化防止)
		if self.decision == False:
			pass
		else:
			self.click = not self.click
		# concern_print()
		# print("After")
		# concern_click_decision()

	def file_read(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global hidden_f
		print("**** hidden : "+str(hidden_f.get()))
		os.chdir(self.curdir)
		new_file_list = list(set(os.listdir()) - set(self.indir))
		# print("再読み込み数 : "+str(len(new_file_list)))
		#再読み込み時に新たに生成されたディレクトリのリスト
		# new_dir_list = list()
		if len(new_file_list) == 0:
			return
		# print(new_file_list)
		for i in range(len(new_file_list)):
			if hidden_f.get() == 0:
				if new_file_list[i][0] != "." and new_file_list[i][0] != "$":
					self.indir.append(new_file_list[i])
			elif hidden_f.get() == 1:
				self.indir.append(new_file_list[i])


	#内部フォルダ表示
	def show_inner(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global showing_indir
		showing_indir = True
		#内部フォルダ表示時のフォルダの周りに表示される、展開方向を決める円
		direction_oval=list()
		#表示された内包フォルダをクリックしても何も起こらないようにする(ただし、clickの値が変化することに注意)
		if not self.decision:
			return
		#表示される内部フォルダは一つだけに制限
		delete=list()
		for i in range(len(oval)):
			if (oval[i].click==False) and (oval[i].decision==False):
				canvas.delete("id_"+str(oval[i].curdir))
				# canvas.delete(oval[i].txt_id)
				delete.append(i)
		for i in delete:
			del oval[delete[0]]
		#内包フォルダを表示
		num=0	#indirのうち確定されていないディレクトリの個数
		# for i in range(len(self.indir)):
		# 	for j in range(len(oval)):
		# 		if self.indir[i] == oval[j].curdir and oval[j].decision == False:
		# 			num+=1

		"""
		修正前:修正後のものと入れ替える
		"""
		move_spiral_dirPath=list()
		# global move_spiral_dirPath
		for i in range(len(self.indir)):

			hyoji=False #decisionと同じ？
			for j in range(len(oval)):
				if oval[j].curdir == str(self.curdir)+"/"+str(self.indir[i]) and oval[j].decision == True:
					hyoji = True
					break
			if hyoji == False:
				# oval.append(Oval(self.x+(50+7*i)*cos(i*60*pi/(180+5*i)), self.y+(50+7*i)*sin(i*60*pi/(180+5*i)), self.indir[i], str(self.curdir) + "/" +str(self.indir[i]),False))
				# oval.append(Oval(self.x+(r_bet_oval+5*i)*cos(i*2*pi/len(self.indir)), self.y+(r_bet_oval+5*i)*sin(i*2*pi/len(self.indir)), self.indir[i], str(self.curdir) + "/" +str(self.indir[i]),False))
				"""螺旋状に配置する場合"""
				# oval.append(Oval(self.x+(r_bet_oval+7*num)*cos(num*60*pi/(180+5*num)), self.y+(r_bet_oval+7*num)*sin(num*60*pi/(180+5*num)), self.indir[i], str(self.curdir) + "/" +str(self.indir[i]),False))
				"""行列形式で配置する場合"""

				num+=1
				move_spiral_dirPath.append(str(self.indir[i]))
		# print("NUM : %d"%len(move_spiral_dirPath))
		# for i in range(num):
		m,n=self.decide_matrix(num)
		for p in range(m):
			for q in range(n):
				if p*n+q<num:
					# direction_oval.append(Dirction_oval(self.x+(folder_width+20)*q, self.y+50+(folder_height+20)*p,r_folder_direction,str(self.curdir) + "/" +str(move_spiral_dirPath[p*n+q])))
					oval.append(Oval(self.x+(folder_width+50)*q, self.y+65+(folder_height+45)*p,move_spiral_dirPath[p*n+q], str(self.curdir) + "/" +str(move_spiral_dirPath[p*n+q]),False, fill_color, edge_color, txt_color))
					"""空白置換"""
					"""
					txt_rearange=re.sub(r'[\s]',"_",str(move_spiral_dirPath[p*n+q]))
					path_rearange=re.sub(r'[\s]',"_",str(self.curdir) + "/" +str(move_spiral_dirPath[p*n+q]))
					oval.append(Oval(self.x+(folder_width+30)*q, self.y+50+(folder_height+30)*p,txt_rearange, path_rearange,False, fill_color, edge_color, txt_color))
					"""






		"""
		修正後
		"""
		"""
		for i in range(len(self.indir)):
			for j in range(len(oval)):
				if self.indir[i] == oval[j].curdir:	#この時点ではインスタンスを新たに生成していないのでoval[j].dcd_under_dirはおそらく不要
					pass
				else:
					oval.append(Oval(self.x+(r_bet_oval+7*num)*cos(num*60*pi/(180+5*num)), self.y+(r_bet_oval+7*num)*sin(num*60*pi/(180+5*num)), self.indir[i], str(self.curdir) + "/" +str(self.indir[i]),False))
					num+=1
		"""

	def decide_matrix(self, num):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		if num<4:
			return 1,num
		else:
			return ceil(num/ceil(sqrt(num))),ceil(sqrt(num))

		# self.move_spiral(0)
	def move_spiral(self,count):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		for i in range(len(move_spiral_dirPath)):
			canvas.move(move_spiral_dirPath[i], 10,0)
		root.after(1000,self.move_spiral(count+1))


	#hide_innerとhide_curdirを一つの関数に統合したい
	def hide_dir(self,list):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		for i in range(len(list)):
			for j in range(len(oval)):
				if oval[i].curdir == oval[j].updir:
					canvas.delete("id_"+str(oval[j].curdir))
					# canvas.delete(oval[j].txt_id)

	#内部フォルダ非表示
	def hide_inner(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		global showing_indir
		showing_indir = False
		delete=list()
		# concern_dir()
		"""
		print("____________________")
		print(str(self.curdir))
		"""
		for i in range(len(oval)):
			# print("  %-2d%-20s\t\t%10s\t\t%-40s"%(i, str(oval[i].updir), str(oval[i].decision), str(oval[i].curdir), str((str(oval[i].updir)==str(self.curdir)))))
			# print("  " + str(i) + "\t" + str(oval[i].updir) + "\t\t" + str(oval[i].decision) + "\t\t" + "%-40s"%str(oval[i].curdir) + "\t" + str((str(oval[i].updir)==str(self.curdir))))
			if str(oval[i].updir)==str(self.curdir) and oval[i].decision==False:		#正常動作確認済み
				# print(str(oval[i].curdir))
				canvas.delete("id_"+str(oval[i].curdir))
				# canvas.delete(oval[i].curdir)
				delete.append(i)
		# print("--------------------\n")
		# for i in reversed(range(len(delete))):
			# del oval[delete[i]]
		for i in reversed(delete):
			del oval[i]



class Line:
	def __init__(self, st_x, st_y, end_x, end_y,tag):
		self.st_x, self.st_y, self.end_x, self.end_y = st_x, st_y, end_x, end_y
		self.tag=tag
		self.id = canvas.create_line(st_x, st_y, end_x, end_y, tags="bbb")
		self.id2 = canvas.create_oval(end_x-3, end_y-3, end_x+3, end_y+3, tags="bbb",fill="Blue")
		canvas.tag_bind("bbb", "<ButtonRelease-2>", self.abc)


	def abc(self, event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		for i in range(len(oval)):
			if self.tag == oval[i].curdir:
				oval[i].hide_direction_oval(event)
				oval[i].which_right_click(event)
				break



#マウスの位置取得
# def move_line(event):
# 	for i in range(len(oval)):
# 		times = sqrt(pow(oval[i].x+r_oval-event.x, 2) + pow(oval[i].y+r_oval-event.y, 2))
# 		if times <= r_oval:
# 			line.insert(0,Line(oval[i].x+r_oval, oval[i].y+r_oval, oval[i].x+r_oval+(event.x-oval[i].x-r_oval)*r_oval/times, oval[i].y+r_oval+(event.y-oval[i].y-r_oval)*r_oval/times))
# 		if len(line)>1:
# 			canvas.delete(line[1].id)
# 			del line[1]
# 	return
# #		canvas.tag_bind(oval[i].oval_id,"<ButtonRelease-1>",oval[i].show_or_hide)
# 		canvas.bind("<ButtonRelease-1>",oval[i].show_or_hide)
# 		canvas.bind("<ButtonRelease-2>",oval[i].move_inner)

def concern_file_dir():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	for i in range(len(oval)):
		print("%-20s%-6s%-6s"%(oval[i].txt,os.path.isdir(oval[i].curdir),os.path.isfile(oval[i].curdir)))
	print("\n")

def concern_click_decision():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	# print("CLICK\tDECISION\tlen : %d\n"%len(oval))
	for i in range(len(oval)):
		print("%-5s"%str(i+1)+"%-30s"%str(oval[i].txt)+"%-60s"%str(oval[i].curdir)+"%-10s"%str(oval[i].click)+"%-10s"%str(oval[i].decision))
	print("\n")



def concern_dcd_under_dir():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	for i in range(len(oval)):
		print(oval[i].curdir)
		print("\t%s"%oval[i].dcd_under_dir)
	print("\n")



def concern_curdir():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	for i in range(len(oval)):
		print(oval[i].curdir)
	print("\n")

def concern_updir():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	for i in range(len(oval)):
		print(oval[i].curdir)
		print("  -> "+oval[i].updir)
		# for j in range(len(oval[i].updir)):
		# 	print("  -> "+str(oval[i].updir))
	print("\n")

def concern_dir():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	for i in range(len(oval)):
		print(str(oval[i].curdir))
		print("  -> "+str(oval[i].indir))
		print("  <- "+str(oval[i].updir))
	print("\n")

def concern_redrawlist():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	print(redraw_list)

def concern_drag():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	print(var.get())

def concern_len():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	print(str(len(oval))+"\t"+str(len(line_betOval)))

def concern_pos():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	print(oval[0].x, oval[0].y)
	"""
	for i in range(len(oval)):
		print(oval[i].x, oval[i].y)
	"""

def concern_funcName(name):
	print("Function : " + str(name))

#mvコマンドに関する一時的な確認ボタン
def click():
	# print("Function : click")
	print(var.get())

#新規作成ボタンが押されたらwindowを表示(dirの新規作成)
def sub_win_new_folder(event=None):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global new_folder_button,sub_win,entry_path
	new_folder_button=True
	sub_win=Toplevel()
	sub_canvas=Canvas(sub_win,width=500,height=100,bg="#ffdddd")

	entry_path=Entry(sub_canvas,width=50,textvariable=buffer1,bg="#eeee99")
	entry_path.delete(0,END)
	entry_path.insert(END,"path")
	entry_path.place(x=10,y=10)

	entry_dir_name=Entry(sub_canvas,width=50,textvariable=buffer2,bg="#eeee99")
	entry_dir_name.delete(0,END)
	entry_dir_name.insert(END,"フォルダ名")
	entry_dir_name.place(x=10,y=40)

	#選択式
	button1=Button(sub_canvas,text="新規作成",command=create_new_dir)
	# button2=Button(sub_canvas,text="新規作成",command=create_new_file)
	button1.place(relx=0.4,rely=0.7)

	sub_canvas.pack(expand=True,fill=BOTH)

def sub_win_new_file(event=None):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global new_folder_button,sub_win,entry_path, file_extention_list
	new_folder_button=True
	sub_win=Toplevel()
	sub_canvas=Canvas(sub_win,width=500,height=100,bg="#ffdddd")

	entry_path=Entry(sub_canvas,width=50,textvariable=buffer1,bg="#eeee99")
	entry_path.delete(0,END)
	entry_path.insert(END,"path")
	entry_path.place(x=10,y=10)

	entry_dir_name=Entry(sub_canvas,width=50,textvariable=buffer2,bg="#eeee99")
	entry_dir_name.delete(0,END)
	entry_dir_name.insert(END,"Dirctry name")
	entry_dir_name.place(x=10,y=40)

	#選択式
	# button1=Button(sub_canvas,text="新規作成",command=create_new_dir)
	button2=Button(sub_canvas,text="新規作成",command=create_new_file)
	button2.place(relx=0.2,rely=0.7)

	#ここからプルダウンボタン
	# val = StringVar()
	# val.set()
	# file_extention_list = ["c", "class", "cpp", "css", "doc", "h", "htm", "html", "java", "js", "ppt", "py", "scr", "txt", "xls"]
	# box = ttk.Combobox(sub_canvas, values = file_extention_list, textvariable=val, state="readonly")
	# box = ttk.Combobox(sub_canvas, values = ("拡張子を選択", "aif", "aiff", "ani", "au", "avi", "bak", "bat", "bin", "bmp", "c", "cgi", "chm", "class", "cpe", "cpp", "css", "dat", "doc", "com", "dat", "dcr", "dic", "dir", "dll", "doc", "dxr", "exe", "fon", "fnt", "gif", "h", "hlp", "htm", "html", "ico", "ini", "inf", "java", "jpg", "jpeg", "js", "log", "lzh", "mak", "msg", "mid", "midi", "mov", "mp3", "mpg", "mpeg", "o", "obj", "ocx", "old", "org", "pl", "ppt", "ra", "ram", "reg", "scr", "sys", "tar", "tgz", "tmp", "txt", "vdo", "wav", "wri", "wrl", "xls", "zip"), textvariable=val, state="readonly")
	# box = ttk.Combobox(sub_canvas, values = ("拡張子を選択", "bin", "c", "class", "cpp", "css", "doc", "exe", "gif", "h", "htm", "html", "java", "jpg", "jpeg", "js", "log", "mpg", "mpeg", "o", "ppt", "scr", "tar", "tgz", "tmp", "txt", "xls", "zip"), textvariable=val, state="readonly")
	file_extention_list.sort()
	file_extention_list.insert(0,"拡張子を選択")
	box = ttk.Combobox(sub_canvas, values = file_extention_list, textvariable=val, state="readonly")
	box.current(0) #初期値を"拡張子を選択(index=0)"に設定
	box.place(relx=0.4,rely=0.7)
	# Button(sub_canvas, text="button", command=lambda:print(val.get())).place(relx=0.5,rely=0.5)
	#ここまでプルダウンボタン

	sub_canvas.pack(expand=True,fill=BOTH)

#新規作成ウィンドウを削除
def create_new_dir():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global buffer1,buffer2
	if (buffer1.get()=="") or (buffer2.get()==""):
		m.showerror('showerror',"入力が不足しています")
	else:
		buff=re.sub(r'[\s]',"\ ",str(buffer2.get()))
		# try:
		# print("***"+str(buffer1.get())+"***")
		os.chdir(str(buffer1.get()))
		os.mkdir(str(buff))
		"""
		print("***"+str(os.getcwd())+"***")
		subprocess.call("cd %s/"%str(buffer1.get()),shell=True)
		print("***"+str(os.getcwd())+"***")
		# except:
			# info_path = exc_info()[1]
			# m.showerror('showerror',"指定したディレクトリは存在しません")
		# try:
		subprocess.call("mkdir %s"%str(buff),shell=True)
		# except:
			# info_name = exc_info()[1]
			# m.showerror('showerror',"ファイル名が無効です")
		"""
		#新規作成したフォルダーに対してパスを修正
		for i in range(len(oval)):
			if oval[i].curdir == str(buffer1.get()):
				oval[i].indir.append(str(buff))

		sub_win.destroy()
#新規作成したディレクトリを表示できるようにovalに追加!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#新規作成ウィンドウを削除
def create_new_file():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	pass
	global buffer1,buffer2
	if (buffer1.get()=="") or (buffer2.get()==""):
		m.showerror('showerror',"入力が不足しています")
	else:
		if val.get() == "拡張子を選択":
			buff=re.sub(r'[\s]',"\ ",str(buffer2.get()))
		else:
			buff=re.sub(r'[\s]',"\ ",str(buffer2.get()))+"."+str(val.get())
		os.chdir(str(buffer1.get()))
		f = open("%s"%str(buff),"w")
		f.close
		"""
		# try:
		subprocess.call("cd %s/"%str(buffer1.get()),shell=True)
		# except:
			# info_path = exc_info()[1]
			# m.showerror('showerror',"指定したディレクトリは存在しません")
		# try:
		subprocess.call("touch %s"%str(buff),shell=True)
		# except:
			# info_name = exc_info()[1]
			# m.showerror('showerror',"ファイル名が無効です")
		"""
		for i in range(len(oval)):
			if oval[i].curdir == str(buffer1.get()):
				oval[i].indir.append(str(buff))
		sub_win.destroy()
		# oval.append(Oval())

def sub_win_search(event=None):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global new_folder_button,sub_win,entry_path
	new_folder_button=True
	sub_win=Toplevel()
	sub_canvas=Canvas(sub_win,width=500,height=100,bg="#ffdddd")

	entry_path=Entry(sub_canvas,width=50,textvariable=buffer1,bg="#eeee99")
	entry_path.delete(0,END)
	entry_path.insert(END,"path")
	entry_path.place(x=10,y=10)

	entry_dir_name=Entry(sub_canvas,width=50,textvariable=buffer2,bg="#eeee99")
	entry_dir_name.delete(0,END)
	entry_dir_name.insert(END,"Dirctry name")
	entry_dir_name.place(x=10,y=40)

	#選択式
	# button1=Button(sub_canvas,text="新規作成",command=create_new_dir)
	button2=Button(sub_canvas,text="検索",command=search)
	button2.place(relx=0.3,rely=0.7)
	sub_canvas.pack(expand=True,fill=BOTH)


def list_clicked(self,event):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	pass
	# listbox = event.widget
 #    indexes = listbox.curselection()
 #    item = listbox.get(indexes[0])
 #    print(item)



#検索
def search():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global buffer1,buffer2
	global searching
	searching = True
	found_path_list = list()
	path = str(buffer1.get())
	name = str(buffer2.get())
	# subprocess.call("mdfind -onlyin %s %s"%(str(buffer1.get()),str(buffer2.get())), shell=True)
	out = subprocess.check_output(["mdfind","-onlyin",path, name]).decode('utf-8')
	msg = "Not found" if out == "" else out
	# m.showerror("showerror", msg)
	# print("探しているもの")
	# print(msg)



	#確定されたディレクトリ内検索

	for i in range(out.count("\n")):
		found_path_list.append(out.split("\n")[i])

	"""
	for i in range(len(found_path_list)):
		# print(found_path_list[i].split(str(home_dir)+"/")[1])
		print(found_path_list[i].split(str(path))[1].split("/",2)[1])
		for j in range(len(oval)):
			if oval[j].curdir == path+"/"+found_path_list[i].split(str(path))[1].split("/",2)[1]:
				canvas.itemconfigure(oval[j].oval_id, fill="Blue")
	"""

	os.chdir(path)
	folder = os.listdir()
	# print("現在のディレクトリの中にある候補")
	# print(folder)
	path2=path

	for i in range(len(found_path_list)):
		hilight(path,found_path_list[i],i,len(found_path_list))
	"""
	for i in range(len(found_path_list)):
		for j in range(found_path_list[i].count("/")-path2.count("/")):
			folder=os.listdir()
		# print(found_path_list[i].split(str(path)+"/",1)[1])
			dir=path2+"/"+found_path_list[i].split(str(path2)+"/",1)[1].split("/",1)[0]
			print("次に探しに行くべきディレクトリ")
			print(dir)
			os.chdir(dir)
			path2=dir
	"""
		# for j in range(len(oval)):
		# 	if oval[j].curdir == dir and oval[j].decision==True:
		# 		canvas.itemconfigure(oval[j].oval_id, fill="Blue")
		# 		print("###")
		# 		print(oval[j].curdir)

# w/2,h/2,"test",os.getcwd(),True

	"""
	for i in range(len(oval)):
		for j in range(len(found_path_list)):
			if oval[i].curdir == found_path_list[j] and oval[i].curdir in found_path_list[j]:
				canvas.itemconfigure(oval[i].oval_id, fill="Blue")
	"""

# search_path以下のディレクトリのうち目的の方向をハイライト
def hilight(search_path,find_path,n,all):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	os.chdir(search_path)
	folder=os.listdir()
	hyoji=False
	new_oval_list=list()
	for i in range(len(folder)):
		if find_path.count(search_path+"/"+folder[i])==1:
			for j in range(len(oval)):
				if search_path+"/"+folder[i] == oval[j].curdir:
					hyoji=True
					if oval[j].decision == True:
						canvas.itemconfigure("id_"+oval[j].curdir, fill=str(fill_color))
						canvas.itemconfigure(oval[j].txt_id, fill=str(txt_color))
					else:
						print(str(oval[j].curdir+" は確定されたディレクトリではありません"))
					break
			if hyoji==False:
				# print("追加")
				# print(search_path+"/"+folder[i])
				# print("\n")
				if new_oval_list.count(search_path+"/"+folder[i])==0:
					new_oval_list.append(str(search_path)+"/"+str(folder[i]))
	# print("---")
	# print(new_oval_list)
	for i in range(len(new_oval_list)):
		for j in range(len(oval)):
			if new_oval_list[i].rsplit("/",1)[0] == oval[j].curdir:
				# print(oval[j].curdir)
				line_betOval.append(Line_betOval(oval[j].x, oval[j].y, oval[j].x+r_bet_oval*cos(2*pi*n/all), oval[j].y+r_bet_oval*sin(2*pi*n/all), new_oval_list[i]))
				"""空白置換"""
				"""
				line_betOval.append(Line_betOval(oval[j].x, oval[j].y, oval[j].x+r_bet_oval*cos(2*pi*n/all), oval[j].y+r_bet_oval*sin(2*pi*n/all), re.sub(r'[\s]',"_",new_oval_list[i])))
				"""
				# canvas.tag_lower(line_betOval[-1].line_bet_id)
				canvas.tag_lower("lineId_"+line_betOval[-1].oval_path)
				oval.append(Oval(oval[j].x+r_bet_oval*cos(2*pi*n/all), oval[j].y+r_bet_oval*sin(2*pi*n/all), new_oval_list[i].rsplit("/",1)[1], new_oval_list[i], True, fill_color, edge_color, txt_color))
				"""空白置換"""
				"""
				txt_rearange=re.sub(r'[\s]',"_",new_oval_list[i].rsplit("/",1)[1])
				path_rearange=re.sub(r'[\s]',"_",new_oval_list[i])
				oval.append(Oval(oval[j].x+r_bet_oval*cos(2*pi*n/all), oval[j].y+r_bet_oval*sin(2*pi*n/all), txt_rearange, path_rearange, True, fill_color, edge_color, txt_color))
				"""
				# line_betOval.append(Line_betOval(oval[j].x+r_oval*cos(2*pi*n/all), oval[j].y+r_oval*sin(2*pi*n/all), oval[j].x+(r_bet_oval-r_oval)*cos(2*pi*n/all), oval[j].y+(r_bet_oval-r_oval)*sin(2*pi*n/all), new_oval_list[i]))

				canvas.itemconfigure("id_"+oval[-1].curdir, fill=str(fill_color))
				canvas.itemconfigure(oval[-1].txt_id, fill=str(txt_color))
				for k in range(len(new_oval_list[i].split(home_dir)[1].split("/"))-1):
					for l in range(len(oval)):
						if oval[l].curdir == new_oval_list[i].rsplit("/",k+1)[0]:
							# print(oval[l].curdir)
							oval[l].dcd_under_dir.append(new_oval_list[i])
							break




	# next_search_dir=search_path+"/"+found_path_list[i].split(str(path)+"/",1)[1].split("/",1)[0]






#削除用サブウィンドウ

def sub_win_remove(event=None):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global new_folder_button,sub_win,entry_path
	new_folder_button=True
	sub_win=Toplevel()
	sub_canvas=Canvas(sub_win,width=500,height=70,bg="#ffdddd")

	entry_path=Entry(sub_canvas,width=50,textvariable=buffer1,bg="#eeee99")
	entry_path.delete(0,END)
	entry_path.insert(END,"path")
	entry_path.place(x=10,y=10)

	#ダミー
	"""
	entry_dir_name=Entry(sub_canvas,width=50,textvariable=buffer2,bg="#eeee99")
	entry_dir_name.delete(0,END)
	entry_dir_name.insert(END,"Dirctry name")
	entry_dir_name.place(x=10,y=40)
	"""

	# button1=Button(sub_canvas,text="新規作成",command=create_new_dir)
	button1=Button(sub_canvas,text="削除",command=remove)
	button1.place(relx=0.4,rely=0.6)

	sub_canvas.pack(expand=True,fill=BOTH)

#サブウィンドウで選択されたファイルの削除
def remove():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	# global entry_path
	q=m.askyesno("AAAAA", "Yes No")
	if q:
		path = str(buffer1.get())		#削除対象ディレクトリのパスを取得
		# print(path)

		"""
		ここで選択されたディレクトリをFinder+の表示から削除
		"""
		for i in reversed(range(len(oval))):
			# print("RMV-"+str(oval[i].curdir))
			if oval[i].curdir == path:
				oval[i].hide_delete()

			# oval[i].search_dir(oval[i].curdir)
		print("Function : Re remove")

		"""
		ここから選択されたディレクトリをTerminal上から削除
		"""
		r_buff = re.sub(r'[\s]',"\ ",str(buffer1.get()))
		# print("BUFF : "+r_buff)
		r_path, r_name = r_buff.rsplit("/",1)
		# print("path : "+r_path)
		# print("name : "+r_name)
		# print("cmd  : "+"rm", "-r", "%s"%str(r_name))
		r_nam = " ".join(["-r",str(r_name)])
		# print(r_nam)
		#subprocess.call("cd %s"%str(r_path),shell=True)
		os.chdir(r_path)
		# print(os.getcwd())
		"""
		osモジュールではtree構造の再帰的削除ができない
		"""
		"""
		try:
			subprocess.call("rm -d %s"%str(r_nam),shell=True)
		except:
			subprocess.call("rm -f %s"%str(r_nam),shell=True)
		"""

		if os.path.isdir(path):
			sh.rmtree(path)
		else:
			subprocess.call("rm -f %s"%str(r_nam),shell=True)
		for i in range(len(oval)):
			oval[i].refresh_dir()
		sub_win.destroy()
	else:
		return


#新規作成windowが閉じられた時に、fill等を元に戻す
def rollback():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global new_folder_button
	new_folder_button=False
	for i in range(len(selected_oval)):
		canvas.delete(selected_oval[i])
	# for i in range(len(oval)):
		# canvas.itemconfigure(oval[i].oval_id,fill=bg_color)


def scroll_start(event):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	dist(none,event)
	"""
	print("Function : scroll_start")
	global scroll_start_x, scroll_start_y
	if drag==False:
		canvas.scan_mark(event.x, event.y)
		# canvas.
		scroll_start_x, scroll_start_y = event.x , event.y
		# print(scroll_start_x,scroll_start_y)
	"""
	global scroll_start_x, scroll_start_y
	if drag==False:
		canvas.scan_mark(event.x, event.y)
		scroll_start_x, scroll_start_y = xscroll.get()[0], yscroll.get()[0]
		# canvas.

		# print(scroll_start_x,scroll_start_y)

def scrooling(event):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global scroll_start_x, scroll_start_y, scroll
	scroll = True
	if drag==False:
		# print(canvas.bbox(oval[0].oval_id))
		# print(event.x, event.y)
		# print(scroll_start_x)
		# print("Doing : scrolling")
		scroll = True
		for i in range(len(oval)):
			oval[i].x += (xscroll.get()[0]-scroll_start_x)*(scrollX*2+w)
		canvas.scan_dragto(event.x, event.y, gain=1)
		# print(event.x-scroll_start_x, event.y-scroll_start_y)

		# for i in range(len(oval)):
		# 	oval[i].x += event.x-scroll_start_x
		# 	oval[i].y += event.y-scroll_start_y
		# scroll_start_x = event.x
		# scroll_start_y = event.y

def scroll_end(event):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global scroll_start_x, scroll_start_y, scroll, drag
	# if scroll == True:
	# 	print("**********")
		# for i in range(len(oval)):
			# oval[i].x = (canvas.bbox(oval[i].oval_id)[0]+canvas.bbox(oval[i].oval_id)[2])/2
			# oval[i].y = (canvas.bbox(oval[i].oval_id)[1]+canvas.bbox(oval[i].oval_id)[3])/2
			# oval[i].x =
			# oval[i].y =
			# canvas.move("id_"+oval[i].curdir,event.x-scroll_start_x,event.y-scroll_start_y)
			# oval[i].x += event.x-scroll_start_x
			# oval[i].y += event.y-scroll_start_y
			# scroll_start_x, scroll_start_y = event.x, event.y
			# scroll = False
	# else:
	# 	scroll_start_x, scroll_start_y = event.x, event.y
	# 	scroll = False
	# 	drag = False
	# 	return

def usb():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	os.chdir("/Volumes")
	files = os.listdir()
	print(files)
	for i in range(len(files)):
		if files[i]!="Macintosh HD" and files[i]!="MobileBackups":
			print("###")
			print(canvas.winfo_width())
			oval.append(Oval(canvas.winfo_width()/2,100,str(files[i]),"/Volumes/"+str(files[i]),True,fill_color,edge_color,txt_color))
		if i==len(files)-1 and (files[i]=="Macintosh HD" or files[i]=="MobileBackups"):
			m.showerror("Error","外部ディスクが接続されていません")
	os.chdir(str(home_dir))

# 隠しファイルの表示・非表示
def show_hidden_files():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)

# メインウィンドウの初期化
def initialization():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	for i in reversed(range(1,len(oval))):
		canvas.delete("id_"+str(oval[i].curdir))
		for j in range(len(line_betOval)):
			if line_betOval[j].oval_path == oval[i].curdir:
				# canvas.delete(line_betOval[j].line_bet_id)
				canvas.delete("lineId_"+line_betOval[j].oval_path)
		del(oval[i])
	del(line_betOval[:])

def callback():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)

def set_color_window():
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	global new_folder_button, sub_win,entry_path
	# global scale_R, scale_G, scale_B
	# サブウィンドウのサイズ
	this_windowX, this_windowY = 300, 500
	# サンプルディレクトリの表示位置（中心座標）
	sample_folder_x, sample_folder_y = this_windowX/2, 100
	# 選択されたディレクトリの色
	fill_col, edge_col = fill_color, edge_color
	for i in range(len(oval)):
		if oval[i].curdir == buffer1:
			fill_col = oval[i].fill_color
			edge_col = oval[i].edge_color
			break
	new_folder_button = True
	sub_win=Toplevel()
	sub_canvas=Canvas(sub_win,width=this_windowX,height=this_windowY,bg="#ddddff")

	# パスのエントリーボックス作成
	entry_path=Entry(sub_canvas,width=50,textvariable=buffer1,bg="#eeee99")
	entry_path.delete(0,END)
	entry_path.insert(END,"path")
	entry_path.place(x=10,y=10)
	txt="Sample"
	#サンプルフォルダの表示
	# xx=sub_canvas.create_polygon(sample_folder_x-folder_width/2, sample_folder_y-folder_height/2-folder_height/7, sample_folder_x-folder_width/2+folder_width*7/22, sample_folder_y-folder_height/2-folder_height/7, sample_folder_x-folder_width/2+folder_height/2, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2+folder_height-folder_height/7, sample_folder_x-folder_width/2, sample_folder_y-folder_height/2+folder_height-folder_height/7, width=1, fill=fill_col, outline=edge_col, tags="color_sample")
	# yy=sub_canvas.create_polygon(sample_folder_x-folder_width/2, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2+folder_height, sample_folder_x-folder_width/2, sample_folder_y-folder_height/2+folder_height, width=1, fill=fill_col, outline=edge_col, tags="color_sample")
	# zz=sub_canvas.create_text(sample_folder_x, sample_folder_y, text=txt, tags="color_sample") if len(txt) < 10 else sub_canvas.create_text(sample_folder_x, sample_folder_y, text=txt[0:4]+"\n"+txt[-5:-1], tags="color_sample")
	xx=sub_canvas.create_polygon(sample_folder_x-folder_width/2, sample_folder_y-folder_height/2-folder_height/7, sample_folder_x-folder_width/2+folder_width*7/22, sample_folder_y-folder_height/2-folder_height/7, sample_folder_x-folder_width/2+folder_height/2, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2+folder_height-folder_height/7, sample_folder_x-folder_width/2, sample_folder_y-folder_height/2+folder_height-folder_height/7, width=1, fill=fill_col, outline=edge_col)
	yy=sub_canvas.create_polygon(sample_folder_x-folder_width/2, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2+folder_height, sample_folder_x-folder_width/2, sample_folder_y-folder_height/2+folder_height, width=1, fill=fill_col, outline=edge_col)
	zz=sub_canvas.create_text(sample_folder_x, sample_folder_y, text=txt, tags="color_sample") if len(txt) < 10 else sub_canvas.create_text(sample_folder_x, sample_folder_y, text=txt[0:4]+"\n"+txt[-5:-1])

	"""
	最終的には選択したディレクトリがフォルダならフォルダが、ファイルならファイルの形で表示されるように修正
	"""
	"""
	for i in range(len(oval)):
		if oval[i].curdir == entry_path:
			if os.path.isdir(oval[i].curdir):
				txt=oval[i].txt
				sub_canvas.create_polygon(this_windowX/2-folder_width/2, this_windowY/2-folder_height/2-folder_height/7, this_windowX/2-folder_width/2+folder_width*7/22, this_windowY/2-folder_height/2-folder_height/7, this_windowX/2-folder_width/2+folder_height/2, this_windowY/2-folder_height/2, this_windowX/2-folder_width/2+folder_width, this_windowY/2-folder_height/2, this_windowX/2-folder_width/2+folder_width, this_windowY/2-folder_height/2+folder_height-folder_height/7, this_windowX/2-folder_width/2, this_windowY/2-folder_height/2+folder_height-folder_height/7, width=1, fill="#eeeeee", outline="#000000", tags="color_sample")
				sub_canvas.create_polygon(this_windowX/2-folder_width/2, this_windowY/2-folder_height/2, this_windowX/2-folder_width/2+folder_width, this_windowY/2-folder_height/2, this_windowX/2-folder_width/2+folder_width, this_windowY/2-folder_height/2+folder_height, this_windowX/2-folder_width/2, this_windowY/2-folder_height/2+folder_height, width=1, fill="#eeeeee", outline="#000000", tags="color_sample")
			elif os.path.isfile(oval[i].curdir):
				sub_canvas.create_polygon(this_windowX/2-file_width/2, this_windowY/2-file_height/2, this_windowX/2-file_width/2+file_width*5/9, this_windowY/2-file_height/2, this_windowX/2+file_width/2, this_windowY/2-file_height/2+file_width*5/9, this_windowX/2+file_width/2, this_windowY/2+file_height/2, this_windowX/2-file_width/2, this_windowY/2+file_height/2, width=1, fill="#eeeeee", outline="#000000", tags="color_sample")
			break
	sub_canvas.create_text(this_windowX/2, this_windowY/2, text=txt, tags="color_sample") if len(txt) < 10 else sub_canvas.create_text(this_windowX/2, this_windowY/2, text=txt[0:4]+"\n"+txt[-5:-1], tags="color_sample")
	"""

	# RGBカラーを設定するスクロールバーの作成



	sub_canvas.pack(expand=True,fill=BOTH)
	# scale_R = Scale(sub_canvas,label="Red",orient="h",from_=0,to=255,resolution=1,command=func(sub_canvas))
	# scale_G = Scale(sub_canvas,label="Green",orient="h",from_=0,to=255,resolution=1,command=func(sub_canvas))
	# scale_B = Scale(sub_canvas,label="Blue",orient="h",from_=0,to=255,resolution=1,command=func(sub_canvas))
	# scale_R = Scale(sub_canvas,label="Red",orient="h",from_=0,to=255,resolution=1)
	# scale_G = Scale(sub_canvas,label="Green",orient="h",from_=0,to=255,resolution=1)
	# scale_B = Scale(sub_canvas,label="Blue",orient="h",from_=0,to=255,resolution=1)
	global scale_R,scale_G,scale_B
	sub_canvas.tag_bind(scale_R,"<Button1-Motion>",func(sub_canvas,scale_R.get(),scale_G.get(),scale_B.get(),xx,yy,zz))
	sub_canvas.tag_bind(scale_G,"<Button1-Motion>",func(sub_canvas,scale_R.get(),scale_G.get(),scale_B.get(),xx,yy,zz))
	sub_canvas.tag_bind(scale_B,"<Button1-Motion>",func(sub_canvas,scale_R.get(),scale_G.get(),scale_B.get(),xx,yy,zz))

	scale_R.place(relx=0.3,rely=0.5)
	scale_G.place(relx=0.3,rely=0.6)
	scale_B.place(relx=0.3,rely=0.7)
	# sub_canvas.pack(expand=True,fill=BOTH)
"""
def set_color_window():
	print("Function : set_color_window")
	sub_win_set_color=Toplevel()
	# sub_canvas=Canvas(sub_win_set_color,width=800,height=600,bg="#ffffff")
	scrollbar = Scrollbar(sub_win_set_color)
	scrollbar.pack(side = RIGHT, fill = Y)
	oval_list = Listbox(sub_win_set_color, yscrollcommand = scrollbar.set)
	fill_color_list = Listbox(sub_win_set_color, yscrollcommand = scrollbar.set)
	edge_color_list = Listbox(sub_win_set_color, yscrollcommand = scrollbar.set)
	for i in range(len(oval)):
		oval_list.insert(END, oval[i].curdir)
		fill_color_list.insert(END, oval[i].fill_color)
		edge_color_list.insert(END, oval[i].edge_color)
	print()
	oval_list.pack(side = LEFT, fill = BOTH)
	fill_color_list.pack(side = LEFT, fill = BOTH)
	edge_color_list.pack(side = LEFT, fill = BOTH)
	scrollbar.config(command = oval_list.xview)
	scrollbar.config(command = fill_color_list.xview)
	scrollbar.config(command = edge_color_list.xview)
	# sub_canvas.pack(expand=False,fill=BOTH)
"""

def func(sub_canvas,r,g,b,xx,yy,zz):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	# print(r,g,b)
	# global entry_path
	# r,g,b = scale_R.get(), scale_G.get(), scale_B.get()
	# sub_canvas.itemconfigure(fill="#%02x%02x%02x"%(scale_R.get(),scale_G.get(),scale_B.get()))
	sub_canvas.itemconfigure(xx,fill="#%02x%02x%02x"%(r,g,b))
	# sub_canvas.itemconfigure(outline="#%02x%02x%02x"%(scale_R.get(),scale_G.get(),scale_B.get()))

# カラー設定ウィンドウのクラス
class Window:
	def __init__(self):
		global new_folder_button, sub_win,entry_path
		# global scale_R, scale_G, scale_B
		# サブウィンドウのサイズ
		this_windowX, this_windowY = 500, 250
		# サンプルディレクトリの表示位置（中心座標）
		sample_folder_x, sample_folder_y = this_windowX/2, 100
		# 選択されたディレクトリの色
		self.fill_col, self.edge_col, self.txt_col = fill_color, edge_color, txt_color
		# メインウィンドウ上の選択されたフォルダの各カラーを取得
		for i in range(len(oval)):
			if oval[i].curdir == buffer1.get():
				self.fill_col = oval[i].fill_color
				self.edge_col = oval[i].edge_color
				self.txt_col = oval[i].txt_color
				break

		new_folder_button = True
		sub_win=Toplevel()
		self.sub_canvas=Canvas(sub_win,width=this_windowX,height=this_windowY,bg="#ddddff")

		# パスのエントリーボックス作成
		entry_path=Entry(self.sub_canvas,width=50,textvariable=buffer1,bg="#eeee99")
		entry_path.delete(0,END)
		entry_path.insert(END,"path")
		entry_path.place(x=10,y=10)
		txt="Sample"
		#サンプルフォルダの表示
		# xx=sub_canvas.create_polygon(sample_folder_x-folder_width/2, sample_folder_y-folder_height/2-folder_height/7, sample_folder_x-folder_width/2+folder_width*7/22, sample_folder_y-folder_height/2-folder_height/7, sample_folder_x-folder_width/2+folder_height/2, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2+folder_height-folder_height/7, sample_folder_x-folder_width/2, sample_folder_y-folder_height/2+folder_height-folder_height/7, width=1, fill=fill_col, outline=edge_col, tags="color_sample")
		# yy=sub_canvas.create_polygon(sample_folder_x-folder_width/2, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2+folder_height, sample_folder_x-folder_width/2, sample_folder_y-folder_height/2+folder_height, width=1, fill=fill_col, outline=edge_col, tags="color_sample")
		# zz=sub_canvas.create_text(sample_folder_x, sample_folder_y, text=txt, tags="color_sample") if len(txt) < 10 else sub_canvas.create_text(sample_folder_x, sample_folder_y, text=txt[0:4]+"\n"+txt[-5:-1], tags="color_sample")
		self.xx=self.sub_canvas.create_polygon(sample_folder_x-folder_width/2, sample_folder_y-folder_height/2-folder_height/7, sample_folder_x-folder_width/2+folder_width*7/22, sample_folder_y-folder_height/2-folder_height/7, sample_folder_x-folder_width/2+folder_height/2, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2+folder_height-folder_height/7, sample_folder_x-folder_width/2, sample_folder_y-folder_height/2+folder_height-folder_height/7, width=1, fill=self.fill_col, outline=self.edge_col,tag="sample_color")
		self.yy=self.sub_canvas.create_polygon(sample_folder_x-folder_width/2, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2, sample_folder_x-folder_width/2+folder_width, sample_folder_y-folder_height/2+folder_height, sample_folder_x-folder_width/2, sample_folder_y-folder_height/2+folder_height, width=1, fill=self.fill_col, outline=self.edge_col,tag="sample_color")
		self.zz=self.sub_canvas.create_text(sample_folder_x, sample_folder_y, text=txt, tags="sample_color_txt", fill=self.txt_col) if len(txt) < 10 else sub_canvas.create_text(sample_folder_x, sample_folder_y, text=txt[0:4]+"\n"+txt[-5:-1], fill=self.txt_col, tags="sample_color_txt")

		"""
		self.scale_fill_R = Scale(self.sub_canvas,label="Red",orient="h",from_=0,to=255,resolution=1,command=self.ttt)
		self.scale_fill_G = Scale(self.sub_canvas,label="Green",orient="h",from_=0,to=255,resolution=1,command=self.ttt)
		self.scale_fill_B = Scale(self.sub_canvas,label="Blue",orient="h",from_=0,to=255,resolution=1,command=self.ttt)
		# self.scale_A = Scale(self.sub_canvas,label="Tranceparent",orient="h",from_=0,to=255,resolution=1,command=self.ttt)
		self.scale_edge_R = Scale(self.sub_canvas,label="Red",orient="h",from_=0,to=255,resolution=1,command=self.ttt)
		self.scale_edge_G = Scale(self.sub_canvas,label="Green",orient="h",from_=0,to=255,resolution=1,command=self.ttt)
		self.scale_edge_B = Scale(self.sub_canvas,label="Blue",orient="h",from_=0,to=255,resolution=1,command=self.ttt)
		"""
		self.sub_canvas.pack(expand=True,fill=BOTH)
		"""
		self.scale_fill_R.place(relx=0.1,rely=0.5)
		self.scale_fill_G.place(relx=0.1,rely=0.6)
		self.scale_fill_B.place(relx=0.1,rely=0.7)
		# self.scale_A.place(relx=0.3,rely=0.8)
		self.scale_edge_R.place(relx=0.6,rely=0.5)
		self.scale_edge_G.place(relx=0.6,rely=0.6)
		self.scale_edge_B.place(relx=0.6,rely=0.7)
		"""
		fill_col_button=Button(self.sub_canvas,text="塗りつぶしの色",command=self.fill_selector)
		edge_col_button=Button(self.sub_canvas,text="輪郭の色",command=self.edge_selector)
		text_col_button=Button(self.sub_canvas,text="文字の色",command=self.text_selector)
		button1=Button(self.sub_canvas,text="反映",command=self.reflect)
		fill_col_button.place(relx=0.1,rely=0.55)
		edge_col_button.place(relx=0.4,rely=0.55)
		text_col_button.place(relx=0.6,rely=0.55)
		button1.place(relx=0.44,rely=0.7)
		# button2=CheckButton(self.sub_canvas,text="一括",command=self.)


	def fill_selector(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		selected = askcolor(title="", color=fill_color)
		if selected[1] != None:
			self.fill_col = selected[1]
			self.sub_canvas.itemconfigure("sample_color",fill=selected[1])

	def edge_selector(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		selected = askcolor(title="", color=edge_color)
		if selected[1] != None:
			self.edge_col = selected[1]
			self.sub_canvas.itemconfigure("sample_color",outline=selected[1])

	def text_selector(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		selected = askcolor(title="", color=txt_color)
		if selected[1] != None:
			self.txt_col = selected[1]
			self.sub_canvas.itemconfigure("sample_color_txt",fill=selected[1])

	def ttt(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		# print(self.scale_fill_R.get(), self.scale_fill_G.get(), self.scale_fill_B.get())
		self.sub_canvas.itemconfigure("sample_color",fill="#%02x%02x%02x"%(self.scale_fill_R.get(), self.scale_fill_G.get(), self.scale_fill_B.get()))
		self.sub_canvas.itemconfigure("sample_color_txt",fill="#%02x%02x%02x"%(self.scale_edge_R.get(), self.scale_edge_G.get(), self.scale_edge_B.get()))

	# メインウィンドウのフォルダに対して色の更新を行う
	# ただし、ovalクラスの__init__において、tagによってテキストとポリゴンを一つにしているため例外処理が必要
	def reflect(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		for i in range(len(oval)):
			if oval[i].curdir == buffer1.get():
				canvas.itemconfigure(oval[i].oval_id,fill=self.fill_col)
				canvas.itemconfigure(oval[i].oval_id,outline=self.edge_col)
				canvas.itemconfigure(oval[i].txt_id,fill=self.txt_col)
				oval[i].fill_color = self.fill_col
				oval[i].edge_color = self.edge_col
				oval[i].txt_color = self.txt_col
				try:
					canvas.itemconfigure(oval[i].oval_id2,fill=self.fill_col)
					canvas.itemconfigure(oval[i].oval_id2,outline=self.edge_col)

				except:
					pass

				# canvas.itemconfigure("id_"+oval[i].curdir,fill="#%02x%02x%02x"%(self.scale_fill_R.get(), self.scale_fill_G.get(), self.scale_fill_B.get()))
				# canvas.itemconfigure(oval[i].txt_id,fill="#%02x%02x%02x"%(self.scale_edge_R.get(), self.scale_edge_G.get(), self.scale_edge_B.get()))

# フォルダに対して画像を読み込む
class load_image:
	"""
	画像のリサイズを行う場合
	"""
	"""
	def __init__(self):
		global entry_path, new_folder_button, sub_win
		new_folder_button=True
		self.this_windowX, self.this_windowY = 500, 600
		margin_x, margin_y = 100,100
		image_width, image_height = 300, 300*9/11
		# 画像の中心座標
		self.x, self.y = 100, 300
		# 画像ドラッグ時の画像の中心とマウスの差
		self.error_posx, self.error_posy = 0, 0
		# 画像四隅のポイントの中心とマウスの差
		self.point_error_posx, self.point_error_posy = 0,0
		# 画像四隅のポイントの中心座標
		self.point_NW_x, self.point_NW_y = margin_x, margin_y
		self.point_NE_x, self.point_NE_y = margin_x+image_width, margin_y
		self.point_SE_x, self.point_SE_y = margin_x+image_width, margin_y+image_height
		self.point_SW_x, self.point_SW_y = margin_x, margin_y+image_height

		sub_win=Toplevel()
		self.sub_canvas=Canvas(sub_win,width=self.this_windowX, height=self.this_windowY,bg="#eeeeee")
		self.sub_canvas.pack()
		self.filename=askopenfilename(filetypes = [("Image Files", (".gif", ".ppm")),("GIF Files", ".gif"),("PPM Files", ".ppm")],initialdir = "~/Desktop")
		# self.image_data = PhotoImage(file=self.filename,width=int(folder_width),height=int(folder_height))
		self.image_data = PhotoImage(file=self.filename)
		# パスバー
		entry_path=Entry(self.sub_canvas,width=30,textvariable=buffer1,bg="#eeee99")
		entry_path.delete(0,END)
		entry_path.insert(END,"Path name")
		# 確定ボタン
		button1=Button(self.sub_canvas,text="確定",command=self.put_image)

		# self.sub_canvas.create_rect(0,0,this_windowX,this_windowY,fill="#ffffff")

		around_color = "#aaaaaa"
		self.image=self.sub_canvas.create_image(self.x,self.y,image=self.image_data)
		self.margin_N=self.sub_canvas.create_polygon(0,0,self.this_windowX,0,self.this_windowX,margin_x,0,margin_y,fill="#aaaaaa")
		self.margin_E=self.sub_canvas.create_polygon(margin_x+image_width,0,self.this_windowX,0,self.this_windowX,self.this_windowY,margin_x+image_width,self.this_windowY,fill="#aaaaaa")
		self.margin_S=self.sub_canvas.create_polygon(0,margin_y+image_height,self.this_windowX,margin_y+image_height,self.this_windowX,self.this_windowY,0,self.this_windowY,fill="#aaaaaa")
		self.margin_W=self.sub_canvas.create_polygon(0,0,margin_x,0,margin_x,self.this_windowY,0,self.this_windowY,fill="#aaaaaa")
		point_radius=4
		point_color="#0000ff"
		self.point_NW=self.sub_canvas.create_oval(self.point_NW_x-point_radius,self.point_NW_y-point_radius,self.point_NW_x+point_radius,self.point_NW_y+point_radius,fill=point_color,tags="point_NW")
		self.point_NE=self.sub_canvas.create_oval(self.point_NE_x-point_radius,self.point_NE_y-point_radius,self.point_NE_x+point_radius,self.point_NE_y+point_radius,fill=point_color,tags="point_NE")
		self.point_SE=self.sub_canvas.create_oval(self.point_SE_x-point_radius,self.point_SE_y-point_radius,self.point_SE_x+point_radius,self.point_SE_y+point_radius,fill=point_color,tags="point_SE")
		self.point_SW=self.sub_canvas.create_oval(self.point_SW_x-point_radius,self.point_SW_y-point_radius,self.point_SW_x+point_radius,self.point_SW_y+point_radius,fill=point_color,tags="point_SW")
		# self.sub_canvas.create_polygon(100,100,300,100,300,300,100,300,width=1)

		self.sub_canvas.tag_bind(self.image,"<1>",self.drag)
		self.sub_canvas.tag_bind(self.image,"<B1-Motion>",self.move)


		# ファイルやフォルダの縦横比と画像の縦横比を合わせないといけない
		# self.sub_canvas.tag_bind("point_NW","<B1-Motion>",self.resize_start_NW)
		# self.sub_canvas.tag_bind("point_NE","<B1-Motion>",self.resize_start_NE)
		# self.sub_canvas.tag_bind("point_SE","<B1-Motion>",self.resize_start_SE)
		# self.sub_canvas.tag_bind("point_SW","<B1-Motion>",self.resize_start_SW)
		# self.sub_canvas.tag_bind("point_NW","<B1-Motion>",self.resize_NW)
		# self.sub_canvas.tag_bind("point_NE","<B1-Motion>",self.resize_NE)
		# self.sub_canvas.tag_bind("point_SE","<B1-Motion>",self.resize_SE)
		# self.sub_canvas.tag_bind("point_SW","<B1-Motion>",self.resize_SW)


		entry_path.place(x=10,y=10)
		button1.place(relx=0.5,rely=0.9)
		sub_win.mainloop()
	"""
	"""
	画像のリサイズを行わない場合
	"""
	def __init__(self):
		global entry_path, new_folder_button, sub_win
		new_folder_button=True
		self.this_windowX, self.this_windowY = 300, 200
		# 画像の中心座標
		self.x, self.y = self.this_windowX/2, self.this_windowY/2
		sub_win=Toplevel()
		self.sub_canvas=Canvas(sub_win,width=self.this_windowX, height=self.this_windowY,bg="#eeeeee")
		self.sub_canvas.pack()
		self.sub_canvas.create_rectangle(self.this_windowX/2-folder_width/2, self.this_windowY/2-folder_height/2, self.this_windowX/2+folder_width/2, self.this_windowY/2+folder_height/2, fill="White")
		# self.oval_id2		= canvas.create_polygon(x-folder_width/2, y-folder_height/2, x-folder_width/2+folder_width, y-folder_height/2, x-folder_width/2+folder_width, y-folder_height/2+folder_height, x-folder_width/2, y-folder_height/2+folder_height, width=1, fill=fill_color, outline=edge_color, tags="id_"+str(self.curdir))
		self.filename=askopenfilename(filetypes = [("Image Files", (".gif", ".ppm")),("GIF Files", ".gif"),("PPM Files", ".ppm")],initialdir = "~/Desktop")
		# self.image_data = PhotoImage(file=self.filename,width=int(folder_width),height=int(folder_height))
		self.image_data = PhotoImage(file=self.filename)
		# パスバー
		entry_path=Entry(self.sub_canvas,width=30,textvariable=buffer1,bg="#eeee99")
		entry_path.delete(0,END)
		entry_path.insert(END,"path")
		# 確定ボタン
		button1=Button(self.sub_canvas,text="確定",command=self.put_image)

		# self.sub_canvas.create_rect(0,0,this_windowX,this_windowY,fill="#ffffff")

		around_color = "#aaaaaa"
		self.image=self.sub_canvas.create_image(self.x,self.y,image=self.image_data)
		self.sub_canvas.tag_bind(self.image,"<1>",self.drag)
		self.sub_canvas.tag_bind(self.image,"<B1-Motion>",self.move)
		entry_path.place(x=10,y=10)
		button1.place(relx=0.4,rely=0.8)
		sub_win.mainloop()


	def drag(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.error_posx, self.error_posy = event.x-self.x, event.y-self.y


	def move(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.sub_canvas.move(self.image,event.x-self.x-self.error_posx, event.y-self.y-self.error_posy)
		self.x = event.x - self.error_posx
		self.y = event.y - self.error_posy
		# print(self.x,self.y)

	def resize_start_NW(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.point_error_posx, self.point_error_posy = event.x-self.point_NW_x, event.x-self.point_NW_y

	def resize_start_NE(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.point_error_posx, self.point_error_posy = event.x-self.point_NE_x, event.x-self.point_NE_y

	def resize_start_SE(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.point_error_posx, self.point_error_posy = event.x-self.point_SE_x, event.x-self.point_SE_y

	def resize_start_SW(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.point_error_posx, self.point_error_posy = event.x-self.point_SW_x, event.x-self.point_SW_y

	def resize_NW(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.sub_canvas.coords(self.margin_N,0,0,self.this_windowX,0,self.this_windowX,event.y-self.point_error_posy,0,event.y-self.point_error_posy)
		self.sub_canvas.coords(self.margin_W,0,0,event.x-self.point_error_posx,0,event.x-self.point_error_posx,self.this_windowY,0,self.this_windowY)
		self.sub_canvas.move(self.point_NW,event.x-self.point_NW_x-self.point_error_posx,event.y-self.point_NW_y-self.point_error_posy)
		self.sub_canvas.move(self.point_NE,0,event.y-self.point_NE_y-self.point_error_posy)
		self.sub_canvas.move(self.point_SW,event.x-self.point_SW_x-self.point_error_posx,0)
		self.point_NW_x = event.x-self.point_error_posx
		self.point_NW_y = event.y-self.point_error_posy
		self.point_NE_y = event.y-self.point_error_posy
		self.point_SW_x = event.x-self.point_error_posx


	def resize_NE(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.sub_canvas.coords(self.margin_N,0,0,self.this_windowX,0,self.this_windowX,event.y-self.point_error_posy,0,event.y-self.point_error_posy)
		self.sub_canvas.coords(self.margin_E,event.x-self.point_error_posx,0,self.this_windowX,0,self.this_windowX,self.this_windowY,event.x-self.point_error_posx,self.this_windowY)
		self.sub_canvas.move(self.point_NE,event.x-self.point_NE_x-self.point_error_posx,event.y-self.point_NE_y-self.point_error_posy)
		self.sub_canvas.move(self.point_NW,0,event.y-self.point_NW_y-self.point_error_posy)
		self.sub_canvas.move(self.point_SE,event.x-self.point_SE_x-self.point_error_posx,0)
		self.point_NE_x = event.x-self.point_error_posx
		self.point_NE_y = event.y-self.point_error_posy
		self.point_NW_y = event.y-self.point_error_posy
		self.point_SE_x = event.x-self.point_error_posx

	def resize_SE(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.sub_canvas.coords(self.margin_S,0,event.y-self.point_error_posy,self.this_windowX,event.y-self.point_error_posy,self.this_windowX,self.this_windowY,0,self.this_windowY)
		self.sub_canvas.coords(self.margin_E,event.x-self.point_error_posx,0,self.this_windowX,0,self.this_windowX,self.this_windowY,event.x-self.point_error_posx,self.this_windowY)
		self.sub_canvas.move(self.point_SE,event.x-self.point_SE_x-self.point_error_posx,event.y-self.point_SE_y-self.point_error_posy)
		self.sub_canvas.move(self.point_SW,0,event.y-self.point_SW_y-self.point_error_posy)
		self.sub_canvas.move(self.point_NE,event.x-self.point_NE_x-self.point_error_posx,0)
		self.point_SE_x = event.x-self.point_error_posx
		self.point_SE_y = event.y-self.point_error_posy
		self.point_SW_y = event.y-self.point_error_posy
		self.point_NE_x = event.x-self.point_error_posx


	def resize_SW(self,event):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		self.sub_canvas.coords(self.margin_S,0,event.y-self.point_error_posy,self.this_windowX,event.y-self.point_error_posy,self.this_windowX,self.this_windowY,0,self.this_windowY)
		self.sub_canvas.coords(self.margin_W,0,0,event.x-self.point_error_posx,0,event.x-self.point_error_posx,self.this_windowY,0,self.this_windowY)
		self.sub_canvas.move(self.point_SW,event.x-self.point_SW_x-self.point_error_posx,event.y-self.point_SW_y-self.point_error_posy)
		self.sub_canvas.move(self.point_SE,0,event.y-self.point_SE_y-self.point_error_posy)
		self.sub_canvas.move(self.point_NW,event.x-self.point_NW_x-self.point_error_posx,0)
		self.point_SW_x = event.x-self.point_error_posx
		self.point_SW_y = event.y-self.point_error_posy
		self.point_SE_y = event.y-self.point_error_posy
		self.point_NW_x = event.x-self.point_error_posx

	# メインウィンドウのフォルダに画像を貼り付ける
	"""
	・画像を貼り付けた際に、画像をフォルダと同様移動できるようにする
	・画像の大きさを加工して貼り付けることはできるのか
	・少なくとも画像のリサイズは他のアプリケーションで行ってもらうとして、画像に対してもidを与えるように修正
	"""
	def put_image(self):
		if funcName: concern_funcName(sys._getframe().f_code.co_name)
		# print(buffer1.get())
		for i in range(len(oval)):
			if oval[i].curdir == buffer1.get():
				test=canvas.create_image(oval[i].x,oval[i].y,image=self.image_data,tags="id_"+oval[i].curdir)

# ファイルの新規作成時にプルダウンメニューに表示される拡張子の設定を行う
"""
拡張子を追加する場合、file_extention_list[0]が日本語なので最初に取り除き、
そこに新たな拡張子を加え、アルファベット順でソートし、最後にfole_extention_list[0]
を追加する。
"""
class set_file_extention:
	print("class : set_file_extention")
	def __init__(self):
		print("Function : set_file_extention -> init")

# 選択されたパスを自動展開
def auto_expand(auto_expand_path):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	home_depth = home_dir.count("/")
	depth = auto_expand_path.count("/")
	# print(depth)
	"""
	for i in range(depth-3):
		for j in range(len(oval)):
			if oval[j].curdir.count("/")-3 == i:
				print(oval[j].curdir.rsplit("/",i)[0])
				if oval[j].curdir.rsplit("/",i)[0] == auto_expand_path.rsplit("/",i)[0]:
					print(oval[j].curdir.rsplit("/",i)[0])
				else:
					for k in range(len(oval)):
						if oval[k].
					oval.append(Oval())
			# elif j == len(oval)-1:
				# oval.append(Oval)
	"""
	# print("The number of times to search")
	est=False #サイドバーより選択されたディレクトリがすでにあるかどうか
	parent_dir=list() # あたらに追加したovalの親ディレクトリのdcd_under_dirを追加する
	new_dir=list()	# 新たに作られたovalのパス
	for i in reversed(range(depth-home_depth)):
		est=False
		for j in range(len(oval)):
			if oval[j].curdir == auto_expand_path.rsplit("/",i)[0]:
				est=True
		if est==False:
			# 親ディレクトリの探索
			for j in range(len(oval)):
				if oval[j].curdir == auto_expand_path.rsplit("/",i)[0].rsplit("/",1)[0]:
					line_betOval.append(Line_betOval(oval[j].x,oval[j].y,oval[j].x+r_bet_oval,oval[j].y,auto_expand_path.rsplit("/",i)[0]))
					oval.append(Oval(oval[j].x+r_bet_oval,oval[j].y,auto_expand_path.rsplit("/",i)[0].rsplit("/",1)[1],auto_expand_path.rsplit("/",i)[0],True,fill_color,edge_color,txt_color))
					# canvas.tag_lower(line_betOval[-1].line_bet_id)
					canvas.tag_lower("lineId_"+line_betOval[-1].oval_path)
					parent_dir.append(oval[j].curdir)
					new_dir.append(auto_expand_path.rsplit("/",i)[0])

	# 上位ディレクトリのdcd_under_dirにパスを追加
	# print(parent_dir)
	# print(new_dir)
	for i in range(len(parent_dir)):
		for j in range(len(oval)):
			if oval[j].curdir == parent_dir[i]:
				for k in range(i,len(new_dir)):
					if oval[j].curdir != new_dir[k]:
						oval[j].dcd_under_dir.append(new_dir[k])




# サイドバーより選択されたディレクトリのパス取得
def auto_expand_get_path(event):
	if funcName: concern_funcName(sys._getframe().f_code.co_name)
	selection = mylist.curselection()
	value = mylist.get(selection[0])
	# print("selection : "+str(selection)+str(value))
	for i in range(len(quick_path_list)):
		if quick_path_list[i].rsplit("/",1)[1] == value:
			# print("  -> "+quick_path_list[i])
			auto_expand(quick_path_list[i])
			break
		# このif文が実行されることはないはず（実行された時はプログラムミス）
		elif i==len(quick_path_list)-1:
			m.showerror("Error","Error")

def change_size(event):
	# if funcName: concern_funcName(sys._getframe().f_code.co_name)
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    canvas.coords(id_menubar, 0, 0, w, 50)
# def image():
	# a=load_image()
"""

"""
root  = Tk()
root.minsize(200,100)


# ペインウィンドウの設定
pw = PanedWindow(root, sashwidth = 10, orient=HORIZONTAL)

# ここからサイドバー設定
# クイックアクセスバーの初期パス
quick_path_list=["~/Desktop/FinderPlusExperiments/A"]
#
mylist = Listbox(pw, font="MS明朝 16")
for line in range(len(quick_path_list)):
   mylist.insert(END, quick_path_list[line].rsplit("/",1)[1])
mylist.pack( side = LEFT, fill = BOTH, expand=True)
pw.add(mylist)
mylist.bind("<Double-Button-1>",auto_expand_get_path)
# ここまでサイドバー設定




#ウィンドウサイズ
w,h   = 400,400
home_dir = "~/Desktop/FinderPlusExperiments"
#w,h=1000,800	#確認用
# 色指定
bg_color     = "#eeeeee"
fill_color = "#77D2FB"
edge_color = "#000000"
txt_color = "#000000"
#スクロールによってできる仮想座標の大きさ
scrollX, scrollY = 1000, 1000
# canvasにスクロールバーをつける場合
# canvas       = Canvas(frame, width=w, height=h, bg=bg_color, scrollregion=(-scrollX, -scrollY, scrollX+w, scrollY+h))
# canvasにスクロールバーをつけない場合
canvas       = Canvas(root, width=w, height=h, bg=bg_color)
# canvas.pack()
pw.add(canvas)
# メニューバー
id_menubar = canvas.create_rectangle(0,0,w,50,fill="#C9C3BE")
#Ovalクラスの配列
oval         = list()
#円と円の間の線
line_betOval = list()
#redawでドラッグ後に再び書くディレクトリ保管
redraw_list = list()
#ディレクトリの展開方向を決める円のクラスの配列
direction_oval=list()
#mvコマンドや新規作成時のパス自動入力における選択されたディレクトリをハイライト
selected_oval=list()

#oval間の線の色
line_color=["Blue", "Red", "Darkgreen", "Green", "Orange", "Cyan", "Violet"]
#line_colorが何番目まで使われたか
line_color_used_count=0
#ホームディレクトリ下の線の色を決める
line_color_and_path_list=list()
os.chdir(home_dir)
for i in range(len(os.listdir())):
	line_color_and_path_list.append([os.listdir()[i],line_color[i%len(line_color)]])
# print(line_color_and_path_list)

#円と円の中心の間隔（半径）
r_bet_oval   = 100
#円の半径
r_oval       = 20
#フォルダの展開方向を決める円は何番目の円の展開方向を表しているのか
direction_oval_num=0
#マウスが円の中に入ったかどうか
#フォルダの大きさ
folder_width = 40
folder_height = folder_width * 9 / 11
#ファイルの大きさ
file_height = 40
file_width = file_height * 18 / 23
enter_oval   = False
#内部フォルダが表示中かどうか
showing_indir = False
#ディレクトリの展開方向を決める円の半径
r_folder_direction = folder_width/2+10
# image_data=PhotoImage(width = 350, height = 100)
# color_sample = None
# マウスカーソルの位置によって内包フォルダが表示されるのは１つだけ
# show_in=True
#円の内部・外部が変わったか(内部：True, 外部：False)
# change_in=False
# os.chdir("/Users/"+str(os.getlogin()))
#マウスが動いたらmove関数呼び出し
# canvas.bind("<Motion>", move_line)
#mvコマンドに対するボタンの状態
var = IntVar()
var.set(0)
#拡張子の選択
val = StringVar()
#Drag時におけるovalのx,yとマウスの位置の誤差
error_posx=0
error_posy=0
line=list()
#draggingによる移動距離
move_x=0
move_y=0
#スクロール開始時点の座標
scroll_start_x, scroll_start_y = 0, 0
#新規作成ボタンが押されてwindowが表示されているかどうか
new_folder_button=False

# 実行関数の確認
funcName = True

#マウスが押されているかどうかの変数
# press = True
#初期ディレクトリ設定
# os.chdir("/Users/"+str(os.getlogin()))	#本番用
# os.chdir("~/Desktop/test_python")
# oval.append(Oval(w/2,h/2,os.getlogin(),os.getcwd(),True))	#本番用
# os.chdir("~/Documents/MeijiUniv/応用プログラミング演習/test_python")
file_extention_list = ["c", "class", "cpp", "css", "doc", "h", "htm", "html", "java", "js", "ppt", "py", "scr", "txt", "xls"]

# home_dir = "/Users/"+str(os.getlogin())
os.chdir(home_dir)
oval.append(Oval(w/2,h/2,str(home_dir.rsplit("/",1)[1]),os.getcwd(),True,fill_color,edge_color,txt_color))	#確認用
# oval.append(Oval(w/2,h/2,os.getlogin(),os.getcwd(),True))	#本番用

#dragされているかどうか
drag=False
# inline=True
#新規作成ボタンによって新たなwindowが表示されているかどうか
sub_win=None
#検索ウィンドウにおいて検索ボタンが押されたかどうか(押されていない時は検索ボタンを押さない限り検索が始まらない)
searching = False
#スクロールされているかどうか
scroll = False
# 隠しファイルの先頭文字
hidden_files = [".","$"]


#ここからサイドバー定義
"""
side_bar = Scrollbar(root)
# scrollbar.pack( side = RIGHT, fill=Y )
mylist = Listbox(canvas, yscrollcommand = side_bar.set )
# side_bar = Listbox(frame)
for line in range(100):
   # mylist.insert(END, "This is line number " + str(line))
   mylist.insert(END, str(line))

# mylist.pack( side = LEFT, anchor = W, fill = BOTH, ipadx = 1)
# mylist.grid(column=1, ipadx=0)
mylist.place(x=0,y=0)
side_bar.config( command = mylist.xview )
canvas.create_rectangle(300,0,310,h)
"""
#ここまでサイドバー設定



#ここからメインウィンドウの画面設定
canvas.create_text(65,10,text="move_command")
mv_on=Radiobutton(canvas, text="ON",value=1,variable=var)
mv_off=Radiobutton(canvas, text="OFF",value=0,variable=var)
mv_on.place(x=15,y=20)
mv_off.place(x=65,y=20)
# button1=Button(root,text="出力",command=click)
# button1.place(x=150,y=8)
# button2=Button(canvas,text="新規作成(file)",command=sub_win_new_file)
# button5=Button(canvas,text="新規作成(folder)",command=sub_win_new_folder)
# button2.place(x=80,y=8+70)
# button5.place(x=80,y=35+70)
# フォルダの新規作成アイコン
xx=150
yy=30
fw=26
fh=fw*9/11
create_new_folder_button1 = canvas.create_polygon(xx-fw/2, yy-fh/2-fh/7, xx-fw/2+fw*7/22, yy-fh/2-fh/7, xx-fw/2+fh/2, yy-fh/2, xx-fw/2+fw, yy-fh/2, xx-fw/2+fw, yy-fh/2+fh-fh/7, xx-fw/2, yy-fh/2+fh-fh/7, fill="#eeeeee", outline="#000000", tags="create_new_folder_button")
create_new_folder_button2 = canvas.create_polygon(xx-fw/2, yy-fh/2, xx-fw/2+fw, yy-fh/2, xx-fw/2+fw, yy-fh/2+fh, xx-fw/2, yy-fh/2+fh, fill="#eeeeee", outline="#000000", tags="create_new_folder_button")
create_new_folder_button3 = canvas.create_line(xx+fw/2-10,yy-fh+15,xx+fw/2+2,yy-fh+15, fill="Blue", width=3, tags="create_new_folder_button")
create_new_folder_button3 = canvas.create_line(xx+fw/2-4,yy-fh+15-6,xx+fw/2-4,yy-fh+15+6, fill="Blue", width=3, tags="create_new_folder_button")
# canvas.tag_bind("create_new_folder_button","<ButtonRelease-1>",sub_win_new_folder)
canvas.tag_bind("create_new_folder_button","<1>",sub_win_new_folder)
# ファイルの新規作成アイコン
xxx=190
yyy=28
flh=26
flw=flh * 18 / 23
create_new_file_button1 = canvas.create_polygon(xxx-flw/2, yyy-flh/2, xxx-flw/2+flw*5/9, yyy-flh/2, xxx+flw/2, yyy-flh/2+flw*5/9, xxx+flw/2, yyy+flh/2, xxx-flw/2, yyy+flh/2, width=1, fill="#eeeeee", outline="#000000", tags="create_new_file_button")
create_new_file_button3 = canvas.create_line(xxx+flw/2-10,yyy-flh+22,xxx+flw/2+2,yyy-flh+22, fill="Blue", width=3, tags="create_new_file_button")
create_new_file_button3 = canvas.create_line(xxx+flw/2-4,yyy-flh+22-6,xxx+flw/2-4,yyy-flh+22+6, fill="Blue", width=3, tags="create_new_file_button")
canvas.tag_bind("create_new_file_button","<1>",sub_win_new_file)
# button3=Button(root,text="検索",command=search, state=DISABLED)
# button3=Button(canvas,text="検索",command=sub_win_search)
# button3.place(x=250,y=8+70)
# gif1=PhotoImage(file="~/Desktop/FinderPlus.app/spotlight-1.gif")
# search_button = canvas.create_image(220, 30, image=gif1)
search_button1 = canvas.create_oval(225-8, 23-8, 225+8, 23+8, width=3, outline="Black", tags="search_button")
search_button2 = canvas.create_line(225+5, 23+5, 225+15, 23+15, width=3, fill="Black", tags="search_button")
canvas.tag_bind("search_button", "<1>", sub_win_search)
# button4=Button(canvas,text="削除",command=sub_win_remove)
# button4.place(x=304,y=8+70)
remove_button1 = canvas.create_line(260,20, 260,42, 278,42, 278,20, tags="remove_button")
remove_button2 = canvas.create_line(255,20, 283,20, tags="remove_button")
remove_button3 = canvas.create_line(263,20, 263,17, 275,17, 275,20, tags="remove_button")
for i in range(3):
	remove_button4 = canvas.create_line(266+3*i,23, 266+3*i,38, tags="remove_button")
canvas.tag_bind("remove_button", "<1>", sub_win_remove)

entry_path=None
entry_dir_name=None
#パス名
buffer1=StringVar()
buffer1.set("")
#ファイル名
buffer2=StringVar()
buffer2.set("")

#ここまでメインウィンドウの画面設定


# sw=Toplevel()
# sc=Canvas(sw,width=50,height=50)
# scale_R = Scale(sc,label="Red",orient="h",from_=0,to=255,resolution=1)
# scale_G = Scale(sc,label="Green",orient="h",from_=0,to=255,resolution=1)
# scale_B = Scale(sc,label="Blue",orient="h",from_=0,to=255,resolution=1)

#ここからメニューバー設定
hidden_f = IntVar()
hidden_f.set(0)

menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New folder", command=sub_win_new_folder)
filemenu.add_command(label="New file", command=sub_win_new_file)
filemenu.add_command(label="Search", command=sub_win_search)
filemenu.add_command(label="Open...", command=callback)
filemenu.add_separator()
filemenu.add_radiobutton(label="Show HiddenFiles", variable=hidden_f, value=1)
filemenu.add_radiobutton(label="Hide HiddenFiles", variable=hidden_f, value=0)
filemenu.add_command(label="Initialize", command=initialization)
filemenu.add_command(label="USB", command=usb)
filemenu.add_command(label="Exit", command=quit)
setmenu = Menu(menu)
menu.add_cascade(label="Settings", menu=setmenu)
# setmenu.add_command(label="Color", command=set_color_window)
setmenu.add_command(label="Color", command=Window)
# setmenu.add_command(label="Shape", command=set_folder_shape_window)
setmenu.add_command(label="Image", command=load_image)
filemenu.add_separator()
setmenu.add_command(label="File Extention", command=set_file_extention)
helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=callback)
#ここまでメニューバー設定





#ここからスクロール定義

# frame = Frame(canvas)
# xscroll = Scrollbar(frame, orient=HORIZONTAL, command=canvas.xview)
# xscroll.grid(row=1, column=0, sticky=E+W)
# yscroll = Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
# yscroll.grid(row=0, column=1, sticky=N+S)
# canvas.config(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
# canvas.grid(row=0, column=0, sticky=N+E+W+S)
# canvas.grid(sticky=N+E+W+S)
# canvas.bind("<ButtonPress-1>", scroll_start)
# canvas.bind("<B1-Motion>", scrooling)
# canvas.bind("<ButtonRelease-1>", scroll_end)
# canvas.bind("<B1-Motion>", lambda event:print(event.x))
# canvas.bind("<ButtonPress-1>", lambda e:print(xscroll.get()[0]))

# frame.grid_rowconfigure(5, weight=1)
# frame.grid_columnconfigure(0, weight=1)
# frame.grid(sticky=N+E+W+S)

# root.grid_rowconfigure(0, weight=1)
# root.grid_columnconfigure(0, weight=1)

#ここまでスクロール定義
root.bind("<Configure>", change_size)
pw.pack(expand = True, fill = BOTH)
root.mainloop()
