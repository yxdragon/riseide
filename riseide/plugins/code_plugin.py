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
        console.debug('breakpoint', [])
        page.highlight_line(1)
        workspace.on_fresh(None)

class DebugContinue(IDEPlugin):
    name = 'Continue'

    def run(self, app, page, console, workspace, catlog, para):
        console, page = console.get_console(), page.get_page()
        info, status = console.debug('action', ':c')
        page.highlight_line(info['no'])
        workspace.on_fresh(None)

class DebugNext(IDEPlugin):
    name = 'Next'

    def run(self, app, page, console, workspace, catlog, para):
        console, page = console.get_console(), page.get_page()
        info, status = console.debug('action', ':n')
        page.highlight_line(info['no'])
        workspace.on_fresh(None)

class DebugInto(IDEPlugin):
    name = 'Step Into'

    def run(self, app, page, console, workspace, catlog, para):
        console, page = console.get_console(), page.get_page()
        info, status = console.debug('action', ':s')
        page.highlight_line(info['no'])
        workspace.on_fresh(None)

class DebugOut(IDEPlugin):
    name = 'Step Out'

    def run(self, app, page, console, workspace, catlog, para):
        console, page = console.get_console(), page.get_page()
        info, status = console.debug('action', ':r')
        page.highlight_line(info['no'])
        workspace.on_fresh(None)

class DebugStop(IDEPlugin):
    name = 'Debug Stop'

    def run(self, app, page, console, workspace, catlog, para):
        console, page = console.get_console(), page.get_page()
        info, status = console.debug('action', ':q')
        page.highlight_line(info['no'])
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