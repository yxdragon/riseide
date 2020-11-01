import wx, weakref
import wx.lib.agw.flatnotebook as FNB
from .wxconsole import WxConsole

class ConsoleBook(FNB.FlatNotebook):
	def __init__(self, *args, **keys):
		super().__init__(*args, size = (300, 200), agwStyle=0x200|0x8)
		renderer = self._pages._mgr.GetRenderer(0x200|0x8)
		renderer.GetButtonsAreaLength  = lambda x: 160
		renderer.GetLeftButtonPos = lambda x: self.GetClientRect().Width - 140
		renderer.GetRightButtonPos = lambda x: self.GetClientRect().Width - 125
		sizer = wx.BoxSizer( wx.HORIZONTAL )
		sizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		self.btn_new = wx.BitmapButton( self._pages, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, (20, 20), wx.BU_AUTODRAW )
		self.btn_new.SetBitmap( wx.Bitmap( './icons/new.png' ) )
		sizer.Add( self.btn_new, 0, wx.ALIGN_CENTER|wx.ALL, 3 )

		self.btn_restart = wx.BitmapButton( self._pages, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, (20, 20), wx.BU_AUTODRAW )
		self.btn_restart.SetBitmap( wx.Bitmap( './icons/run.png' ) )
		sizer.Add( self.btn_restart, 0, wx.ALIGN_CENTER|wx.ALL, 3 )

		self.btn_clear = wx.BitmapButton( self._pages, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, (20, 20), wx.BU_AUTODRAW )
		self.btn_clear.SetBitmap( wx.Bitmap( './icons/clear.png' ) )
		sizer.Add( self.btn_clear, 0, wx.ALIGN_CENTER|wx.ALL, 3 )

		self.btn_close = wx.BitmapButton( self._pages, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, (20, 20), wx.BU_AUTODRAW )
		self.btn_close.SetBitmap( wx.Bitmap( './icons/close.png' ) )
		sizer.Add( self.btn_close, 0, wx.ALIGN_CENTER|wx.ALL, 3 )
		#sizer.Add( ( 50, 0), 0, wx.EXPAND, 5 )
		self._pages.SetSizer(sizer)
		
		self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.on_closing)
		self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.on_active)
		self.btn_new.Bind(wx.EVT_BUTTON, self.new_console)
		self.btn_clear.Bind(wx.EVT_BUTTON, self.on_clear)
		self.btn_restart.Bind(wx.EVT_BUTTON, self.on_restart)
		self.btn_close.Bind(wx.EVT_BUTTON, self.on_close)
		self.workspace = lambda : None
		self.new_console(None)

	def reference(self, workspace):
		self.workspace = weakref.ref(workspace)
		self.get_console().reference(workspace)
		workspace.reference(self.get_console())

	def get_console(self): return self.GetCurrentPage()

	def new_console(self, event, n = [0]):
		n[0] += 1
		self.AddPage( WxConsole(self), 'Console %s'%n, True )

	def on_clear(self, event):
		self.get_console().SetValue('>>> ')

	def on_active(self, event):
		if self.workspace() is None: return
		self.workspace().reference(self.GetPage(event.GetSelection()))
		self.GetPage(event.GetSelection()).reference(self.workspace())

	def on_closing(self, event):
		self.GetPage(event.GetSelection()).terminate()
		if self.GetPageCount()==1: self.new_console(None)
		event.Skip()

	def on_restart(self, event):
		self.GetCurrentPage().restart()

	def on_close(self, event):
		self.DeletePage(self.GetSelection())

if __name__ == '__main__':
	app = wx.App()
	frame = wx.Frame(None)
	cbook = ConsoleBook(frame)
	frame.Show()
	app.MainLoop()
