#!/usr/bin/env python

import  string
import  wx, os, os.path as osp, shutil
from wx.lib.mixins.treemixin import VirtualTree, DragAndDrop, ExpansionState

#---------------------------------------------------------------------------
icons = [
    ('folder.png', []),
    ('img.png', ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'gif']),
    ('txt.png', ['txt']),
    ('html.png', ['html', 'htm']),
    ('markdown.png', ['md']),
    ('py.png', ['py']),
    ('json.png', ['json']),
    ('unknown.png', [])]

class TreeView(VirtualTree, ExpansionState, wx.TreeCtrl):
    def __init__(self, parent, *args, **key):
        super(TreeView, self).__init__(parent, *args, **key)
        self.SetSize(300, -1)
        self.event_switch = True
        self.roots = ['root', True, []]
        self.il = il = wx.ImageList(16, 16)
        for name, exts in icons:
            il.Add(wx.Bitmap('./icons/%s'%name).ConvertToImage().Rescale(16,16).ConvertToBitmap())

        self.SetImageList(il)
        self.handle = print

        class OpenDrop(wx.FileDropTarget):
            def __init__(self, win): 
                wx.FileDropTarget.__init__(self)
                self.win = win

            def OnDropFiles(self, x, y, path):
                for i in path: self.win.AppendRoot(i)

        self.SetDropTarget(OpenDrop(self))

        self.dragitem, self.loc = None, None
        self.Bind( wx.EVT_LEFT_DOWN, self.OnPress )
        self.Bind( wx.EVT_MOTION, self.OnMove )
        self.Bind( wx.EVT_TREE_ITEM_RIGHT_CLICK, self.PopMenu)
        self.Bind( wx.EVT_TREE_SEL_CHANGED, self.OnSelected)
        self.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self.Bind( wx.EVT_TREE_END_LABEL_EDIT, self.OnRename)

    def OnActivate(self, event):
        index = self.GetIndexOfItem(event.GetItem())
        path = self.GetPathByIndex(index)
        self.handle(path, True)

    def OnSelected(self, event):
        index = self.GetIndexOfItem(event.GetItem())
        path = self.GetPathByIndex(index)
        self.handle(path, False)

    def RefreshItems(self):
        VirtualTree.RefreshItems(self)

    def RefreshStatus(self):        
        self.event_switch = False
        lst = self.GetItemChildren(self.GetRootItem())
        for i in range(100000):
            if i == len(lst): break
            idx = self.GetIndexOfItem(lst[i])
            obj = self.GetContByIndex(idx)
            lst.extend(self.GetItemChildren(lst[i]))
            if obj[1]: self.Expand(lst[i])
            else: self.Collapse(lst[i])
        self.event_switch = True

    def SetHandler(self, handle=print):
        self.handle = handle

    def IsExpanded(self, item):
        return self.GetContByIndex(self.GetIndexOfItem(item))[1]

    def OnPress(self, event):
        p = wx.Point(event.GetX(), event.GetY())
        item, _, _ = self.HitTest(p, alwaysReturnColumn=True)
        if not item: item = self.GetRootItem()
        if self.GetCount() == 0: return
        index = self.GetIndexOfItem(item)
        if len(index)==1:
            self.dragitem = item
            self.loc = index
            print(self.dragitem)
        else:
            pass
            #self.printf()
            # self.RefreshStatus()
        event.Skip()

    def PopMenu(self, event):
        self.CreatMenu(event.GetItem())

    def OnMove(self, event):
        if not event.LeftIsDown(): self.dragitem = None
        if not self.dragitem: return event.Skip()
        p = wx.Point(event.GetX(), event.GetY())
        item = self.HitTest(p)[0] or self.GetRootItem()
        index = self.GetIndexOfItem(item)
        if len(index) > 1: return
        if len(index)==0: index = (len(self.roots[2])-1,)

        if self.loc[0] != index[0]: 
            target = self.roots[2].pop(self.loc[0])
            self.roots[2].insert(index[0], target)
            self.printf()
            self.UnselectAll()
            self.SelectItem(item)
            self.RefreshItems()
            #self.RefreshStatus()
            self.loc = index
        event.Skip()

    def LoadItem(self, item):
        index = self.GetIndexOfItem(item)
        path = self.GetPathByIndex(index)
        name, sta, objs = self.GetContByIndex(index)
        keys, cur = [i[0] for i in objs], os.listdir(path)
        for i in cur:
            full = osp.join(path, i)
            if i in keys: continue
            if osp.isdir(full): objs.insert(-1, [i, False, [['', False, None]]])
            else: objs.insert(-1, [i, False, None])
        for i in [j for j in objs if not j[0] in cur and j[0]!='']: objs.remove(i)

    def SortItem(self, item):
        index = self.GetIndexOfItem(item)
        name, sta, objs = self.GetContByIndex(index)
        path = self.GetPathByIndex(index)
        lst = sorted([(osp.isfile(osp.join(path, i[0])), i[0], i) for i in objs])
        for i in range(len(objs)): objs[i] = lst[(i+1)%len(lst)][2]

    def OnItemExpanding(self, event):
        if not self.event_switch: return
        item = event.GetItem()
        self.LoadItem(item)
        self.SortItem(item)
        VirtualTree.OnItemExpanding(self, event)
        idx = self.GetIndexOfItem(item)
        self.GetContByIndex(idx)[1] = True
        # self.RefreshItems()

    def OnItemCollapsed(self, event):
        if not self.event_switch: return
        if not self.IsExpanded(event.GetItem()): return
        index = self.GetIndexOfItem(event.GetItem())
        path, obj = '', self.roots
        for i in index: 
            path, obj = osp.join(path, obj[2][i][0]), obj[2][i]
        obj[1] = False
        chs = [0 if not i[2] else len(i[2])-1 for i in obj[2]]
        if sum(chs)==0: 
            del obj[2][:-1]
            # self.RefreshItems()
            print('delete node')
        VirtualTree.OnItemCollapsed(self, event)
        # self.RefreshItems()

    def OnGetChildrenCount(self, index):
        name, sta, obj = self.roots
        for i in index: name, sta, obj = obj[i]
        return 0 if obj is None else len(obj)

    def OnGetItemText(self, index, column=0):
        obj = self.roots
        for i in index: obj = obj[2][i]
        return osp.split(obj[0])[-1]

    def OnGetItemImage(self, index, which=wx.TreeItemIcon_Normal, column=0):
        path = self.GetPathByIndex(index)
        if path[-1]=='/': return -1
        if osp.isdir(path): return 0
        name = osp.split(path)[-1]
        if name=='':return -1
        n, e = osp.splitext(name)
        for i, (name, ext) in enumerate(icons):
            if e[1:] in ext: return i
        return len(icons)-1

    def GetPathByIndex(self, index):
        name, sta, obj = self.roots
        path = ''
        for i in index:
            name, sta, obj = obj[i]
            path += '/' + name
        return path[1:]

    def GetContByIndex(self, index):
        obj = self.roots
        for i in index: obj = obj[2][i]
        return obj

    def AppendRoot(self, path):
        if path in [i[0] for i in self.roots[2]]:
            print('已经存在')
            return
        if osp.isdir(path): self.roots[2].append([path, False, [['', False, None]]])
        else: self.roots[2].append((path, False, None))
        self.RefreshItems()

    def CreatMenu(self, item):
        idx = self.GetIndexOfItem(item)
        menu = wx.Menu()
        # Show how to put an icon in the menu
        events = [('创建文件', lambda e, p=item:self.OnNewFile(item)),
                  ('创建目录', lambda e, p=item:self.OnNewFolder(item)),
                  ('打开所在路径', lambda e, p=item:self.OnOpen(item)),
                  ('重命名', lambda e, p=item:self.EditLabel(item)),
                  ('删除', lambda e, p=item:self.OnDelete(item)),
                  ('移除目录', lambda e, p=item:self.OnRemove(item))]

        if len(self.GetIndexOfItem(item))!=1: events.pop(-1)
        for title, f in events:
            im = wx.MenuItem(menu, wx.NewId(), title)
            self.Bind(wx.EVT_MENU, f, im)
            menu.Append(im)

        self.PopupMenu(menu)
        menu.Destroy()

    def rename(self, old, new):
        print(old, new)

    def remove(self, path):
        print(path)

    def printf(self, obj=None, layer=(0,)):
        obj = obj or self.roots
        print('\t'*len(layer), obj[1], obj[0])
        if obj[2] is None: return
        for i in range(len(obj[2])):
            self.printf(obj[2][i], layer+(i,))

    def OnNewFolder(self, item):
        index = self.GetIndexOfItem(item)
        path = self.GetPathByIndex(index)
        if osp.isfile(path):
            path = osp.split(path)[0]
            index = index[:-1]
        os.mkdir(path + '/New Folder')
        if self.IsExpanded(item):
            _, _, cont = self.GetContByIndex(index)
            cont.insert(0, ['New Folder', False, [['', False, None]]])
            self.RefreshItems()
            self.EditLabel(self.GetItemByIndex(index+(0,)))

    def OnNewFile(self, item):
        index = self.GetIndexOfItem(item)
        path = self.GetPathByIndex(index)
        if osp.isfile(path):
            path = osp.split(path)[0]
            index = index[:-1]
        open(path + '/newfile', 'w').close()

        if self.IsExpanded(item):
            _, _, cont = self.GetContByIndex(index)
            cont.insert(0, ['newfile', False, None])
            self.RefreshItems()
            self.EditLabel(self.GetItemByIndex(index+(0,)))

    def OnRename(self, event):
        item = event.GetItem()
        index = self.GetIndexOfItem(item)
        label = event.GetLabel()
        path = self.GetPathByIndex(index)
        npath = osp.split(path)[0]+'/'+label
        print(path, npath)
        
        if path == npath: return
        try:
            os.rename(path, npath)
            self.GetContByIndex(index)[0] = label
        except:
            print('请关闭该目录下打开的文件')
            return event.Veto()
        if len(index)==1: return
        pitem = self.GetItemByIndex(index[:-1])
        self.SortItem(pitem)
        self.RefreshItems()
        event.Veto()

    def OnOpen(self, item):
        index = self.GetIndexOfItem(item)
        path = self.GetPathByIndex(index)
        if osp.isfile(path):
            path = osp.split(path)[0]
        os.startfile(path)

    def OnDelete(self, item):
        items = self.GetSelections()
        parent = []
        for i in items:
            index = self.GetIndexOfItem(i)
            parent.append(index[:-1])
            path = self.GetPathByIndex(index)
            if osp.isdir(path): 
                shutil.rmtree(path)
            else: os.remove(path)
        for i in set(parent):
            pitem = self.GetItemByIndex(i)
            self.LoadItem(pitem)
            self.SortItem(pitem)
        self.RefreshItems()

    def OnRemove(self, item):
        del self.roots[2][self.GetIndexOfItem(item)[0]]
        self.RefreshItems()
#---------------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None)
    TreeView(frame, style = 
        wx.TR_HAS_BUTTONS
       | wx.TR_EDIT_LABELS
       | wx.TR_DEFAULT_STYLE
       | wx.TR_NO_LINES
       | wx.TR_TWIST_BUTTONS
       | wx.TR_MULTIPLE
       | wx.TR_HIDE_ROOT
       | wx.TR_FULL_ROW_HIGHLIGHT)
    frame.Show()
    app.MainLoop()