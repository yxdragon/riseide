import wx, wx.aui, sys
import os.path as osp
sys.path.append('../')
from riseide.consoles import ConsoleBook
from riseide.workspace import WorkSpace
from riseide.codepad import CodePad
from riseide.catlog import TreeView
from riseide.toolbar import ToolBar
from riseide.notebook import ObjectNoteBook

def read_py(path):
    with open(path, encoding='utf-8') as f: return f.read()

ReaderManager = {'py': (read_py, 'code')}

class MiniFrame ( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 881,778 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)

        self.toolbar = ToolBar(self)
        self.init_toolbar()
        self.m_mgr.AddPane( self.toolbar, wx.aui.AuiPaneInfo().Top().CaptionVisible( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).Layer( 1 ) )
        
        '''
        self.toolbar = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT )
        self.btn_start = self.toolbar.AddTool( wx.ID_ANY, u"tool", wx.Bitmap('./console/icons/debug.png'), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )
        self.btn_next = self.toolbar.AddTool( wx.ID_ANY, u"tool", wx.Bitmap('./console/icons/next.png'), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )
        self.btn_step = self.toolbar.AddTool( wx.ID_ANY, u"tool", wx.Bitmap('./console/icons/step.png'), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )
        self.btn_return = self.toolbar.AddTool( wx.ID_ANY, u"tool", wx.Bitmap('./console/icons/return.png'), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )
        self.btn_continue = self.toolbar.AddTool( wx.ID_ANY, u"tool", wx.Bitmap('./console/icons/continue.png'), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )
        self.btn_stop = self.toolbar.AddTool( wx.ID_ANY, u"tool", wx.Bitmap('./console/icons/stop.png'), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )
        self.toolbar.Realize()
        self.m_mgr.AddPane( self.toolbar, wx.aui.AuiPaneInfo().Top().CaptionVisible( False ).PinButton( True ).Gripper().Dock().Resizable().FloatingSize( wx.DefaultSize ).Layer( 1 ) )
        '''

        self.catlog = TreeView(self)
        self.catlog.SetHandler(self.on_open)
        self.m_mgr.AddPane( self.catlog, wx.aui.AuiPaneInfo() .Left() .PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).BestSize( wx.Size( 300,-1 ) ).Layer( 1 ) )

        panel = wx.Panel(self); sizer = wx.BoxSizer( wx.VERTICAL ); self.page = ObjectNoteBook(panel)
        sizer.Add( self.page, 1, wx.EXPAND |wx.ALL, 0 ); panel.SetSizer( sizer )
        self.m_mgr.AddPane( panel, wx.aui.AuiPaneInfo() .Center() .PinButton( True ).Dock().Resizable().CaptionVisible( False ).FloatingSize( wx.DefaultSize ) )

        self.workspace = WorkSpace(self)
        self.m_mgr.AddPane( self.workspace, wx.aui.AuiPaneInfo() .Right() .PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).BestSize( wx.Size( 300,-1 ) ).Layer( 1 ) )

        self.console = ConsoleBook(self)
        self.console.reference(self.workspace)
        self.m_mgr.AddPane( self.console, wx.aui.AuiPaneInfo() .Bottom() .PinButton( True ).Dock().Resizable().FloatingSize( wx.Size( -1,-1 ) ).BestSize( wx.Size( -1,200 ) ) )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        '''
        self.path = './debug/test.py'
        with open(self.path) as f:
            self.page.SetValue(f.read())
            self.page.MarkerSetBackground(0, (255,0,0))
            self.page.MarkerAdd(7, 0)
        '''
        

        '''
        self.toolbar.Bind(wx.EVT_MENU, self.on_debug, self.btn_start)
        self.toolbar.Bind(wx.EVT_MENU, self.on_continue, self.btn_continue)
        self.toolbar.Bind(wx.EVT_MENU, self.on_next, self.btn_next)
        self.toolbar.Bind(wx.EVT_MENU, self.on_return, self.btn_return)
        self.toolbar.Bind(wx.EVT_MENU, self.on_step, self.btn_step)
        self.toolbar.Bind(wx.EVT_MENU, self.on_stop, self.btn_stop)
        '''

    def init_toolbar(self): 
        from riseide.plugins import code_plugin as plg
        tools = [('./icons/全选@1x.png', plg.SelectAll), 
                 ('./icons/运行@1x.png', plg.ExecFile),
                 ('./icons/调试@1x.png', plg.Debug),
                 ('./icons/调试@1x.png', plg.DebugContinue),
                 ('./icons/调试@1x.png', plg.DebugNext),
                 ('./icons/调试@1x.png', plg.DebugInto),
                 ('./icons/调试@1x.png', plg.DebugOut),
                 ('./icons/调试@1x.png', plg.DebugStop)]
        self.toolbar.add_tools(None, tools)

    def on_open(self, path, fixed):
        name, ext = osp.splitext(path)
        reader = ReaderManager.get(ext[1:].lower(), None)
        if reader is None: 
            print('未知格式，无法打开')
            return
        read, tag = reader
        self.show_obj(read(path), path, tag, fixed)

    def show_obj(self, obj, path, tag, fixed):
        if tag=='code':
            self.show_code(obj, path, fixed=fixed)
        if tag=='img':
            self.show_img(obj, path, fixed=fixed)
        if tag=='tab':
            self.show_table(obj, path, fixed=fixed)

    def _show_code(self, cont, path, name, fixed):
        if path != None: name = osp.split(path)[-1]
        codepd = CodePad(self.page, (cont, name, path))
        page = self.page.add_page(codepd, fixed)

    def show_code(self, code, path=None, name='new_script.py', fixed=False):
        wx.CallAfter(self._show_code, code, path, name, fixed)

    def __del__( self ):
        self.m_mgr.UnInit()

if __name__ == '__main__':
    app = wx.App()
    frame = MiniFrame(None)
    frame.Show()
    app.MainLoop()

    # debug('./debug/test.py')
