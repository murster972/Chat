#!/usr/bin/env python3
import os
import urwid

class UI:
	def __init__(self):
		palette = [("title", )]
		self.message = "-- Messages --\n"
		self.input = ""

		palette = [("title", "dark gray", "light gray"), ("msg_display", "dark gray", "white"),
				   ("input", "white", "black"), ("button", "dark blue", "white")]

		divider = urwid.Divider()

		#title
		title_txt = urwid.Text(("title", "CHAT CLIENT - USER-00"), align="center")
		title_txt_map = urwid.AttrMap(title_txt, "title")
		title_divider = urwid.AttrMap(urwid.Divider(), "title")
		title_pile = urwid.Pile([title_divider, title_txt_map, title_divider])

		#displays messages
		self.txt = urwid.Text(("msg_display", self.message))
		txt_padd = urwid.Padding(self.txt, left=1, right=1)
		txt_map = urwid.AttrMap(txt_padd, "msg_display")
		lst_walker = urwid.SimpleListWalker([txt_map])
		lst_box = urwid.ListBox(lst_walker)
		lst_box_map = urwid.AttrMap(lst_box, "msg_display")
		lst_box_divider = urwid.AttrMap(urwid.Divider(), "msg_display")
		lst_box_pile = urwid.Pile([lst_box_divider, lst_box_map])
		#lst_box_filler = urwid.Filler(lst_box_map)
		lst_box_adapt = urwid.BoxAdapter(lst_box_pile, 40)

		#handles users input
		inpt_divider = urwid.AttrMap(urwid.Divider(), "input")
		self.inpt = urwid.Edit(("input", "Message: "))
		inpt_map = urwid.AttrMap(urwid.Padding(self.inpt, left=1, right=1), "input")
		inpt_pile = urwid.Pile([inpt_divider, inpt_map, inpt_divider])

		#button controls
		butn_divider = urwid.AttrMap(urwid.Divider(), "button")
		send_butn = urwid.Button(("button", "Send"))
		send_butn_map = urwid.AttrMap(send_butn, "button")
		active_users_butn = urwid.Button(("button", "Active Users"))
		active_users_butn_map = urwid.AttrMap(active_users_butn, "button")
		close_connection_butn = urwid.Button(("button", "Close Connection"))
		close_connection_butn_map = urwid.AttrMap(close_connection_butn, "button")
		exit_butn = urwid.Button(("button", "Exit"))
		exit_butn_map = urwid.AttrMap(exit_butn, "button")

		butn_pile = urwid.Pile([butn_divider, send_butn_map, active_users_butn_map, close_connection_butn_map, exit_butn_map, butn_divider])

		#Pile container, stacks everything vertically
		top_pile_cont = urwid.Pile([divider, title_pile, lst_box_adapt])
		#top_pile_filler = urwid.Filler(top_pile_cont, valign="top")

		bottom_pile_cont = urwid.Pile([inpt_pile, butn_pile, divider])
		#pile_cont_padd = urwid.Padding(pile_cont, left=2, right=2)
		bottom_pile_filler = urwid.Filler(bottom_pile_cont, valign="top")

		complete_cont = urwid.Pile([top_pile_cont, bottom_pile_filler])
		complete_cont_padd = urwid.Padding(complete_cont, left=2, right=2)

		overlay = urwid.Overlay(complete_cont_padd, urwid.SolidFill(' '), align='center', width=('relative', 60), valign='middle', height=('relative', 60))

		#handles events that occur
		urwid.connect_signal(self.inpt, "change", self.input_change)
		urwid.connect_signal(send_butn, "click", self.send)
		urwid.connect_signal(exit_butn, "click", self.exit_loop)

		loop = urwid.MainLoop(overlay, palette)
		loop.run()

	def send(self, butn):
		self.message += "USER-00: " + self.input + "\n"
		self.txt.set_text(self.message)
		self.inpt.set_edit_text("")

	def input_change(self, input, input_txt):
		self.input = input_txt

	def exit_loop(self, butn):
		raise urwid.ExitMainLoop()

if __name__ == '__main__':
	UI()