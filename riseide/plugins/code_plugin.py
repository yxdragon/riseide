from .base import IDEPlugin, PagePlugin

class SelectAll(PagePlugin):
    name = 'Select All'

    def run(self, app, page, para=None):
        page.get_page().SelectAll()


class ExecFile(IDEPlugin):
    name = 'Run File'

    def run(self, app, page, console, workspace, catlog, para):
        console, page = console.get_console(), page.get_page()
        console.write("execfile('%s')\n"%page.code.path.replace('\\','/'))
        console.pc.write("execfile('%s')"%page.code.path.replace('\\','/'))

class Debug(IDEPlugin):
    name = 'Debug'

    def run(self, app, page, console, workspace, catlog, para):
        console, page = console.get_console(), page.get_page()
        console.write("debug('%s')\n"%page.code.path.replace('\\','/'))
        console.pc.write("debug('%s')"%page.code.path.replace('\\','/'))
        #console.debug('breakpoint', [('./debug/test.py', 8)])
        page.SetSelection(page.PositionFromLine(0), page.GetLineEndPosition(0))
        workspace.on_fresh(None)

'''
 def on_debug(self, event):
        console = self.console.get_console()
        console.write("debug('./debug/test.py')\n")
        console.pc.write("debug('./debug/test.py')")
        console.debug('breakpoint', [('./debug/test.py', 8)])
        self.page.SetSelection(self.page.PositionFromLine(0), self.page.GetLineEndPosition(0))
        self.workspace.on_fresh(None)

    def on_next(self, event):
        info, status = self.console.get_console().debug('action', ':n')
        self.page.SetSelection(self.page.PositionFromLine(info['no']-1), self.page.GetLineEndPosition(info['no']-1))
        self.workspace.on_fresh(None)

    def on_step(self, event):
        info, status = self.console.get_console().debug('action', ':s')
        if status: self.page.SetSelection(
            self.page.PositionFromLine(info['no']-1), self.page.GetLineEndPosition(info['no']-1))
        self.workspace.on_fresh(None)

    def on_return(self, event):
        info, status = self.console.get_console().debug('action', ':r')
        if status: self.page.SetSelection(
            self.page.PositionFromLine(info['no']-1), self.page.GetLineEndPosition(info['no']-1))
        self.workspace.on_fresh(None)

    def on_continue(self, event):
        info, status = self.console.get_console().debug('action', ':c')
        if status: self.page.SetSelection(
            self.page.PositionFromLine(info['no']-1), self.page.GetLineEndPosition(info['no']-1))
        self.workspace.on_fresh(None)

    def on_stop(self, event):
        info, status = self.console.get_console().debug('action', ':q')
        if status: self.page.SetSelection(
            self.page.PositionFromLine(info['no']-1), self.page.GetLineEndPosition(info['no']-1))
        self.workspace.on_fresh(None)
'''