"""A group of classes to extract (optimized) and transform coordinates from .log output files."""

import re
import pandas as pd


class GetCoord:
	"""A class to extract the (optimized) coordinates from a Gaussian output file.
	"""

	def __init__(self, OUTFILE, WORKDIR_PATH='./'):
		self.dict_atm = {'1': 'H', '6': 'C', '7': 'N', '8': 'O', '16': 'S', } # Intentionally truncated.
		self.OUTFILE = OUTFILE
		self.WORKDIR_PATH = WORKDIR_PATH
		self.FILENAME = None
		self.FILEPATH = None
		self.chml = None
		self.coord = None
		self.coord_atnum = None
		self.coord_file = None
		self.coord_raw = None
		self.dser = None
		self.natoms = None


	def _get_file(self):
		"""Transforms `OUTFILE` into a generic file label `FILENAME`.
		"""

		re_file = re.search(r'\w+\.log', self.OUTFILE)
		file = self.OUTFILE[re_file.start():re_file.end()-4]
		self.FILENAME = file
		self.FILEPATH = self.WORKDIR_PATH + file

		return self.FILENAME, self.FILEPATH


	def _get_df(self):
		"""Gets a pandas Series object using `OUTFILE`.
		"""

		try:
			with open(f'{self.OUTFILE}', 'r') as file_out:
				file_lines = file_out.readlines()
			self.dser = pd.Series(file_lines)
			return self.dser

		except FileNotFoundError:
			print(f'Error: No files to pass were found in {self.FILENAME}.log provided.\n')


	def _get_natoms(self):
		"""Gets No. of atoms of the system.
		"""

		re_natoms = re.compile('NAtoms')

		try:
			# Get N of atoms of the sytem (or "supermolecule").
			natoms_idx = self.dser[self.dser.str.contains(re_natoms)].index[0]
			self.natoms = (self.dser[natoms_idx].split())[1]

			return self.natoms

		except IndexError:
			print(f'Error: The file \'{self.OUTFILE}\' might be defective.\n'
				  f'Number of atoms (`NAtoms`) were not found.\n')


	def _get_chml(self):
		"""Gets the charge and multiplicity of the system based on the .log file.
		"""

		re_chml = re.compile(r'Charge =')
		try:
			# Get charge and multiplicity
			chml_idx = self.dser[self.dser.str.contains(re_chml)].index[0]
			chml_ch = (self.dser[chml_idx].split())[2]
			chml_ml = (self.dser[chml_idx].split())[5]
			self.chml = f'{chml_ch} {chml_ml}'

			return self.chml

		except IndexError:
			self.chml = f'0 1'
			print(f'Error: The file \'{self.OUTFILE}.\' might be defective.\n'
					 f'Charge (`Charge`) was not found.\n')

			return self.chml



	def _get_coord(self):
		"""Gets the coordinates of a given .log file.
		"""

		self._get_df()
		self._get_natoms()
		self._get_chml()

		try:
			re_coord = re.compile('Standard orientation:')
			coord_idx = self.dser[self.dser.str.contains(re_coord)].index[-1]
			coord_raw = self.dser.iloc[(coord_idx + 5) : (coord_idx + 5 + int(self.natoms))]
			coord_raw = [atom.split() for atom in coord_raw]
			coord_atnum = [self.dict_atm[str(atnum[1])] for atnum in coord_raw[:]]
			coord_x = [x[3] for x in coord_raw[:]]
			coord_y = [y[3] for y in coord_raw[:]]
			coord_z = [z[3] for z in coord_raw[:]]
			self.coord_file = list(zip(coord_atnum, coord_x, coord_y, coord_z))

			return self.coord_file

		except IndexError:
			pass



class XFile(GetCoord):
	"""A class to create a .xyz file.
	"""

	def __init__(self, OUTFILE, WORKDIR_PATH):
		super().__init__(OUTFILE, WORKDIR_PATH)


	def get_xyz(self):
		super()._get_file()
		super()._get_coord()

		if self.coord_file != None:
			# Write .txt with coordinates
			with open(self.FILEPATH + '.xyz', 'w') as outfile:
				print(f'{self.natoms}\nCoordinates extracted from {self.FILENAME}.log', file=outfile)
				for atm in self.coord_file:
					print(f'{atm[0]}\t {atm[1]}\t {atm[2]}\t {atm[3]}', file=outfile)

			print(f'...Created a .xyz file from \'{self.FILENAME}.log\'.')

		else:
			print(f'There are no coordinates to process for \'{self.OUTFILE}\'.\n')


class GaInpFile(GetCoord):
	"""A class to creates a .com (or .gjf) input file.
	"""

	def __init__(self, OUTFILE, WORKDIR_PATH, mem=12, proc=8, method='pm6', title='Title'):
		super().__init__(OUTFILE, WORKDIR_PATH)
		self.mem = mem
		self.proc = proc
		self.method = method
		self.title = title
		self.head = None


	def head_wrt(self):
		self.head = f'%memory={self.mem}GB\n'
		self.head += f'%nprocshared={self.proc}\n'
		self.head += f'%chk={self.FILENAME}.chk\n'
		self.head += f'# {self.method}\n'
		self.head += f'\n'
		self.head += f'{self.title}. From {self.FILENAME}.log\n'
		self.head += f'\n'
		self.head += f'{self.chml}'

		return self.head


	def get_gainp(self):
		super()._get_file()
		super()._get_coord()
		self.head_wrt()

		if self.coord_file != None:
			# Write .gjf with coordinates
			with open(self.FILEPATH + '.gjf', 'w') as outfile:
				print(f'{self.head}', file=outfile)
				for atm in self.coord_file:
					print(f'{atm[0]}\t {atm[1]}\t {atm[2]}\t {atm[3]}', file=outfile)

			print(f'...Created a .gjf file from \'{self.FILENAME}\'.')

		else:
			print(f'There are no coordinates to process for \'{self.OUTFILE}\'.\n')




class SupInfFile(GetCoord):
	"""A class to create a file in latex-like format containing the coordinates of the file(s) provided.
	"""

	def __init__(self, OUTFILE, WORKDIR_PATH):
		super().__init__(OUTFILE, WORKDIR_PATH)

	def get_si(self):
		super()._get_file()
		super()._get_coord()

		sep1 = r'~'
		sep2 = r'\\'

		if self.coord_file != None:
			# Write .txt with coordinates in a latex-like format.
			with open('./all_geom_coord.txt', 'a') as outfile:
				print(f'{self.natoms} {sep2}\nSystem {sep2}', file=outfile)
				for atm in self.coord_file:
					print(f'{atm[0]} {sep1} {atm[1]} {sep1} {atm[2]} {sep1} {atm[3]} {sep2}', file=outfile)
				print(f'{sep2}\n', file=outfile)

			print(f'...Created a SupInfo .txt file from \'{self.FILENAME}\'.')

		else:
			print(f'There are no coordinates to process for \'{self.OUTFILE}\'.\n')


