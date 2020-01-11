import tkinter as tk

def test_table():
	root = tk.Tk()
	table = HeadlineEntryTable(root, headline=["a", "b", "c", "d", "e"])
	table.grid(row=0, column=0)

	table.set(0, 3, "4")
	table.set(1, 3, "1.5")
	table.set(3, 2, "2.5")
	table.set(4, 0, "3.5")

	table.empty_table()

	table.set(2, 4, "1.5")

	root.mainloop()

class TableRow():
	def __init__(self, parent, row_index, widget_type, num_columns=0, add_button_callback=None, delete_button_callback=None):
		self.parent = parent

		self.buttons = []
		self.columns = []
		self.row_index = row_index

		self.widget_type = widget_type

		for i in range(num_columns):
			self.add_column()

		if add_button_callback != None:
			self.buttons.append(tk.Button(self.parent, text="Add", command=add_button_callback, borderwidth=0, width=3))
			self.buttons[-1].grid(row=self.row_index, column=len(self.columns)+len(self.buttons)-1, sticky="nsew", padx=(1,0), pady=(1,0))

		if delete_button_callback != None:
			self.buttons.append(tk.Button(self.parent, text="Delete", command=lambda: delete_button_callback(self.row_index), borderwidth=0, width=6))
			self.buttons[-1].grid(row=self.row_index, column=len(self.columns) + len(self.buttons) - 1, sticky="nsew", padx=(1,0), pady=(1,0))

	def add_column(self):
		new_widget = self.widget_type(self.parent, text="", borderwidth=0, width=10)

		row = self.row_index
		col = len(self.columns)

		padx = (1,0) if col > 0 else (0,0)
		pady = (1,0) if row > 0 else (0,0)

		new_widget.grid(row=row, column=col, sticky="nsew", padx=padx, pady=pady)

		self.columns.append(new_widget)

		# Move Buttons to end of row
		for i, button in enumerate(self.buttons):
			button.grid(row=self.row_index, column=len(self.columns) + i, sticky="nsew", padx=(1,0), pady=(1,0))

	def forget(self):
		for cell in self.columns:
			cell.grid_forget()

		for button in self.buttons:
			button.grid_forget()

	def move(self, new_row_index):
		self.row_index = new_row_index
		row = self.row_index

		# Move cells
		for i, cell in enumerate(self.columns):
			padx = (1,0) if   i > 0 else (0,0)
			pady = (1,0) if row > 0 else (0,0)

			cell.grid(row=row, column=i, sticky="nsew", padx=padx, pady=pady)

		# Move buttons
		for i, button in enumerate(self.buttons):
			button.grid(row=row, column=len(self.columns) + i, sticky="nsew", padx=(1,0), pady=(1,0))

class TkTable(tk.Frame):
	def __init__(self, parent):
		# use black background so it "peeks through" to 
		# form grid lines
		super().__init__(parent, background="black")

		self._rows = []
		self.num_rows = 0
		self.num_columns = 0

	def _add_row(self, row_index=None, widget_type=tk.Label, add_button_callback=None, delete_button_callback=None):
		if row_index == None:
			# Append row to end of table
			new_row = TableRow(parent=self, row_index=self.num_rows, num_columns=self.num_columns, widget_type=widget_type, add_button_callback=add_button_callback, delete_button_callback=delete_button_callback)
			self._rows.append(new_row)
			self.num_rows += 1
		
		else:
			# Move all rows below the new row one down and reorder self._rows list accordingly
			for i in range(len(self._rows)-1, row_index-1, -1):
				row = self._rows[i]
				row.move(row.row_index+1)

				if i == len(self._rows) - 1:
					self._rows.append(row)
					self.num_rows += 1
				else:
					self._rows[i+1] = row

			# Create new row
			new_row = TableRow(parent=self, row_index=row_index, num_columns=self.num_columns, widget_type=widget_type, add_button_callback=add_button_callback, delete_button_callback=delete_button_callback)
			try:
				self._rows[row_index] = new_row
			except IndexError:
				self._rows.append(new_row)
				self.num_rows += 1

	def _delete_row(self, row_index):
		# Grid-forget the row and delete it's entry in the list
		self._rows[row_index].forget()
		del self._rows[row_index]

		# Move all rows below one up
		for i in range(row_index, len(self._rows)):
			row = self._rows[i]
			row.move(row.row_index-1)

	def _add_column(self):
		for row in self._rows:
			row.add_column()

		self.num_columns += 1

	def empty_table(self):
		for row in self._rows:
			row.forget()
		self._rows = []
		self.num_rows = 0
		self.num_columns = 0

	def set(self, row, column, value, str_format="{}", is_headline=False, add_button_callback=None, delete_button_callback=None, **kwargs):

		# check if the cell already exists
		if len(self._rows) > row:
			if self.num_columns > column:
				# cell exists, change text
				widget = self._rows[row].columns[column]

				widget["text"] = str_format.format(value)
				widget["width"] = len(widget["text"]) + 1

				if is_headline:
					widget["font"] = ("Helvetica", 10, "bold")
				else:
					widget["font"] = ("Helvetica", 10)

				if type(value) == str:
					widget["anchor"] = "w"
					widget["text"] = " " + widget["text"]
				else:
					widget["anchor"] = "e"
					widget["text"] = widget["text"] + " "

				for key, arg in kwargs.items():
					widget[str(key)] = arg
			else:
				self._add_column()
				self.__set(row, column, value, str_format=str_format, is_headline=is_headline, add_button_callback=add_button_callback, delete_button_callback=delete_button_callback, **kwargs)
		else:
			self._add_row(add_button_callback=add_button_callback, delete_button_callback=delete_button_callback)
			self.__set(row, column, value, str_format=str_format, is_headline=is_headline, add_button_callback=add_button_callback, delete_button_callback=delete_button_callback, **kwargs)

	# This is necessary for the recursive function "set" to use this classes implementation
	__set = set

	def prepend_row(self, column_values=list(), str_format="{}", is_headline=False, **kwargs):
		self._add_row(row_index=0)

		# Set values
		for i, value in enumerate(column_values):
			self.set(0, i, value)

	def get_row_as_list(self, row_index):
		return [label["text"] for label in self._rows[row_index].columns]

class HeadlineEntryTable(TkTable):
	def __init__(self, parent, headline=[], add_row_callback=None, delete_row_callback=None):
		super().__init__(parent)

		self.add_row_callback = add_row_callback
		self.delete_row_callback = delete_row_callback

		for col, h_entry in enumerate(headline):
			super().set(0, col, h_entry, is_headline=True)
		super()._add_row(widget_type=tk.Entry, add_button_callback=self.add_entry_row)

	def empty_table(self):
		for row in self._rows[2:]:
			row.forget()
		self._rows = self._rows[:2]
		self.num_rows = len(self._rows)
		self.num_columns = len(self._rows[0].columns)

	def set(self, row, column, value, str_format="{}", is_headline=False, **kwargs):
		# Only change rows with labels, not the row with entries
		if row == 0:
			super().set(row, column, value, str_format=str_format, is_headline=is_headline, **kwargs)
		else:
			super().set(row+1, column, value, str_format=str_format, is_headline=is_headline, delete_button_callback=self._delete_row,  **kwargs)

	def prepend_row(self, column_values=list(), str_format="{}", is_headline=False, **kwargs):
		self._add_row(row_index=2, delete_button_callback=self._delete_row)

		# Set values
		for i, value in enumerate(column_values):
			self.set(1, i, value)

		if self.add_row_callback != None:
			self.add_row_callback(column_values)

	def pop_entries_to_list(self):
		values = []
		for entry in self._rows[1].columns:
			values.append(entry.get())
			entry.delete(first=0, last=tk.END)

		return values

	def add_entry_row(self):
		self.prepend_row(self.pop_entries_to_list())

	def _delete_row(self, row_index):
		column_values = self.get_row_as_list(row_index)

		super()._delete_row(row_index)

		if self.delete_row_callback != None:
			self.delete_row_callback(column_values)
			

if __name__ == "__main__":
	test_table()