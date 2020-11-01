import numpy as np
import pandas as pd
#from consolebook import ConsoleBook
import wx, weakref

class WorkSpace ( wx.Panel ):
    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 300, 500), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )
        sizer = wx.BoxSizer( wx.VERTICAL )
        self.riseup = weakref.ref(parent)
        self.consoles = parent.console
        #sizer.Add( self.consoles, 0, wx.EXPAND, 5 )

        filter = wx.BoxSizer( wx.HORIZONTAL )
        self.chk_array = wx.CheckBox( self, wx.ID_ANY, u"数组", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.chk_array.SetValue(True)
        filter.Add( self.chk_array, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.chk_table = wx.CheckBox( self, wx.ID_ANY, u"表格", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.chk_table.SetValue(True)
        filter.Add( self.chk_table, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.chk_base = wx.CheckBox( self, wx.ID_ANY, u"常规", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.chk_base.SetValue(True)
        filter.Add( self.chk_base, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.chk_all = wx.CheckBox( self, wx.ID_ANY, u"全部", wx.DefaultPosition, wx.DefaultSize, 0 )
        filter.Add( self.chk_all, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        filter.Add( ( 0, 0), 1, wx.EXPAND, 5 )
        self.btn_refresh = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap('./icons/refresh.png'), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        filter.Add( self.btn_refresh, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        sizer.Add( filter, 0, wx.EXPAND, 5 )

        self.lst_table = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT | wx.BORDER_NONE | wx.LC_EDIT_LABELS )
        sizer.Add( self.lst_table, 1, wx.ALL|wx.EXPAND, 5 )
        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"变量：", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer4.Add( self.m_staticText2, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.txt_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.txt_name, 1, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.btn_in = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap('./icons/import.png'), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer4.Add( self.btn_in, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.btn_out = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap('./icons/export.png'), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer4.Add( self.btn_out, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.btn_view = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap('./icons/view.png'), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer4.Add( self.btn_view, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        sizer.Add( bSizer4, 0, wx.EXPAND, 5 )
        self.txt_detail = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,100 ), wx.TE_MULTILINE )
        sizer.Add( self.txt_detail, 0, wx.ALL|wx.EXPAND, 5 )

        self.SetSizer( sizer )
        self.Layout()

        self.lst_table.AppendColumn("变量", wx.LIST_FORMAT_LEFT)
        self.lst_table.AppendColumn("类型", wx.LIST_FORMAT_LEFT)
        self.lst_table.AppendColumn("值", wx.LIST_FORMAT_LEFT)
        self.lst_table.SetColumnWidth(0, 100)
        self.lst_table.SetColumnWidth(1, 100)
        self.lst_table.SetColumnWidth(2, 100)

        self.btn_refresh.Bind(wx.EVT_BUTTON, self.on_fresh)
        self.btn_out.Bind(wx.EVT_BUTTON, self.on_export)
        self.btn_in.Bind(wx.EVT_BUTTON, self.on_import)
        self.lst_table.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        self.btn_view.Bind(wx.EVT_BUTTON, self.on_view)

        self.chk_base.Bind(wx.EVT_CHECKBOX, self.on_fresh)
        self.chk_array.Bind(wx.EVT_CHECKBOX, self.on_fresh)
        self.chk_table.Bind(wx.EVT_CHECKBOX, self.on_fresh)
        self.chk_all.Bind(wx.EVT_CHECKBOX, self.on_fresh)

    def get_filter(self):
        filt = []
        if self.chk_base.GetValue(): filt.extend([int, float, str])
        if self.chk_array.GetValue(): filt.append(np.ndarray)
        if self.chk_table.GetValue(): filt.append(pd.DataFrame)
        if self.chk_all.GetValue(): filt.append('all')
        return filt

    def on_fresh(self, event):
        self.lst_table.DeleteAllItems()
        items, sta = self.consoles.get_console().getobj('locals', self.get_filter())
        for item in items:
            self.lst_table.Append(item)

    def on_select(self, event):
        name = event.GetText()
        obj, status = self.consoles.get_console().getobj('get', name)
        self.txt_name.SetValue(name)
        self.txt_detail.SetValue(repr(obj))

    def on_export(self, event):
        name = self.txt_name.GetValue()
        obj, status = self.consoles.get_console().getobj('get', name)
        self.txt_detail.SetValue(repr(obj))

    def on_import(self, event):
        name = self.txt_name.GetValue()
        obj, status = self.consoles.get_console().getobj('set', (name, self.txt_detail.GetValue()))
        self.txt_detail.SetValue(str(obj))

    def on_view(self, event):
        name = self.txt_name.GetValue()
        obj, status = self.consoles.get_console().getobj('get', name)
        self.txt_detail.SetValue(repr(obj))
        if isinstance(obj, np.ndarray) and obj.ndim in (2,3):
            self.riseup().show_img(obj, path=None, name=name, fixed=True)
        if isinstance(obj, pd.DataFrame):
            self.riseup().show_table(obj, path=None, name=name, fixed=True)

    def __del__( self ):
        pass

if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None)
    WorkSpace(frame)
    frame.Fit()
    frame.Show()
    app.MainLoop()
