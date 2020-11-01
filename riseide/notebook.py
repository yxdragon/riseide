import wx, wx.lib.agw.aui as aui

class ObjectNoteBook(aui.AuiNotebook):
    def __init__(self, parent):
        aui.AuiNotebook.__init__( self, parent, wx.ID_ANY, 
            wx.DefaultPosition, wx.DefaultSize, wx.lib.agw.aui.AUI_NB_DEFAULT_STYLE )
        self.Bind( wx.lib.agw.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_valid) 
        #self.Bind( wx.lib.agw.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_close)
        self.Bind( wx.EVT_IDLE, self.on_idle)
        self.SetArtProvider(aui.AuiSimpleTabArt())
    
    def on_idle(self, event):
        for i in range(self.GetPageCount()):
            panel = self.GetPage(i)
            obj = panel.object
            title = obj.name
            if not panel.fixed: color = (255, 128, 128)
            elif not obj.saved: color = (0, 0, 255)
            else: color = (0, 0, 0)
            if self.GetPageText(i) != title:
                self.SetPageText(i, title)
            if self.GetPageTextColour(i) != color:
                self.SetPageTextColour(i, color)

    def get_page(self, i=None):
        if not i is None: return self.GetPage(i)
        else: return self.GetCurrentPage()
        
    def set_background(self, img):
        self.GetAuiManager().SetArtProvider(ImgArtProvider(img))

    def add_page(self, panel, fixed):
        obj = panel.object
        if fixed:
            # 固定方式载入，且已经打开
            for i in range(self.GetPageCount()):
                if self.GetPage(i).object.path == obj.path:
                    panel.Destroy()
                    self.GetPage(i).fixed = True
                    return self.SetSelection(i)
            # 固定方式载入，但尚未打开
            return self.AddPage(panel, '', True, wx.NullBitmap)
        else:
            # 非固定方式载入，如果已经存在则激活
            for i in range(self.GetPageCount()):
                if self.GetPage(i).object.path == obj.path:
                    panel.Destroy()
                    return self.SetSelection(i)
            # 非固定方式载入，如果不存在，则尝试替换当前非固定
            for i in range(self.GetPageCount()):
                if not self.GetPage(i).fixed:
                    self.DeletePage(i)
                    return self.InsertPage(i, panel, '', True, wx.NullBitmap)
            # 当前没有非固定，则载入新的活动页面
            self.AddPage(panel, '', True, wx.NullBitmap )

    def set_title(self, panel, title):
        self.SetPageText(self.GetPageIndex(panel), title)

    def on_valid(self, event): pass

    def on_close(self, event): pass