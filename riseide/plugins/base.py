class Plugin:
	name = 'Plugin'

	def run(self, app, para):
		print('I am a plugin!')

	def start(self, app, para=None):
		self.run(app, para)

class IDEPlugin:
	name = 'IDEPlugin'

	def run(self, app, page, console, workspace, catlog, para):
		print('I am a ide plugin!')

	def start(self, app, para=None):
		self.run(app, app.page, app.console, app.workspace, app.catlog, para)

class PagePlugin:
	name = 'PagePlugin'

	def run(self, app, page, para):
		print('I am a page plugin!')

	def start(self, app, para=None):
		self.run(app, app.page, para)