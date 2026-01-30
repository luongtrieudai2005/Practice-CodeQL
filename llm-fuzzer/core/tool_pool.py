import subprocess
from pathlib import Path
from typing import Optional, List

class SimpileToolPool:
	""" Tool pool don gian  """

	def __init__(self, libpng_path : str):
		self.libpng_path = Path(libpng_path)

	def get_function_usage_example(self, func_name : str) -> Optional[str]:
		""" Tim usage example cua function trong test files """

		# Tim trong pngtest.c hoac contrib/
		test_files = list(self.libpng_path.glob("**/pngtest*.c"))
		test_files.extend(self.libpng_path.glob("contrib/**/*.c"))

		for test_file in test_files:
			try:
				result = subprocess.run(
					['grep', '-A', '5', '-B', '2', func_name, str(test_file)],
					capture_output=True,
					text=True
				)

				if result.stdout and result.returncode == 0:
					return f"# From {test_file.name}:\n{result.stdout[:500]}"
			except:
				pass

		return None

	def find_init_functions(self, struct_name : str) -> List[str]:
		""" Tim init/create functions cho struct """

		patterns = [
			f'{struct_name}_init',
			f'{struct_name}_create',
			f'png_create_{struct_name}',
			f'png_{struct_name}_init'
		]

		results = []
		for pattern in patterns:
			try:
				grep_result = subprocess.run(
					['grep', '-r', pattern, str(self.libpng_path)],
					capture_output=True,
					text=True
				)

				if grep_result.stdout:
					results.append(pattern)
			except:
				pass
		return results


	