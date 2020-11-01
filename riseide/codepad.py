"""EditWindow class."""

import wx, wx.stc as stc
import os, sys, time, json, re
import sys, keyword
sys.path.append('../')
import jedi

class Code:
    def __init__(self, cont='', name='Code', path=None):
        self.saved = True
        self.path = path
        self.name = name
        self.cont = cont

def get_jedi_comp(content, line, col):
    script = jedi.Script(content, path='temp.py')
    completions = script.complete(line, col)
    comp_list = [com.name for com in completions if len(com.complete)>0]
    return comp_list

def get_jedi_doc(code, line, col):
    script = jedi.Script(code, path='temp.py')
    names = script.help(line, col)
    return names

class CodePad(stc.StyledTextCtrl):
    """EditWindow based on StyledTextCtrl."""

    def __init__(self, parent, code = ('', 'Code', None)):
        """Create EditWindow instance."""
        stc.StyledTextCtrl.__init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.CLIP_CHILDREN | wx.SUNKEN_BORDER)
        self.set_code(Code(*code))
        self.__config()
        
        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)
        self.Bind(stc.EVT_STC_AUTOCOMP_COMPLETED, self.on_autocomp_finish)
        self.fixed = False
        
        # for autocomp
        self.autocomp_once = 0
        self.last_key = -1
        

    def __config(self):
        self.setDisplayLineNumbers(True)
        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, ' '.join(keyword.kwlist))

        self.setStyles()
        self.SetViewWhiteSpace(False)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        # Do we want to automatically pop up command completion options?
        self.autoComplete = True
        self.autoCompleteIncludeMagic = True
        self.autoCompleteIncludeSingle = True
        self.autoCompleteIncludeDouble = True
        self.autoCompleteCaseInsensitive = True
        self.AutoCompSetIgnoreCase(self.autoCompleteCaseInsensitive)
        self.autoCompleteAutoHide = False
        self.AutoCompSetAutoHide(self.autoCompleteAutoHide)
        #self.AutoCompStops(' .,;:([)]}\'"\\<>%^&+-=*/|`')
        # Do we want to automatically pop up command argument help?
        self.autoCallTip = True
        self.callTipInsert = True
        #self.CallTipSetBackground(FACES['calltipbg'])
        #self.CallTipSetForeground(FACES['calltipfg'])
        self.SetWrapMode(False)
        try:
            self.SetEndAtLastLine(False)
        except AttributeError:
            pass
        jedi.preload_module(["numpy", "scipy", "matplotlib"])

    def setDisplayLineNumbers(self, state):
        self.lineNumbers = state
        if state:
            self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
            self.SetMarginWidth(1, 40)
        else:
            # Leave a small margin so the feature hidden lines marker can be seen
            self.SetMarginType(1, 0)
            self.SetMarginWidth(1, 10)

    def setStyles(self):
        with open('style.json') as f: cont = json.loads(f.read())
        def dump(cont):
            title = ['fore','back','face','size','bold','italic']
            idx = [i for i in range(6) if not (cont[i] is None or cont[i] is False)]
            return ','.join(['%s:%s'%(title[i], cont[i]) for i in idx])
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, dump(cont['STYLE_DEFAULT']))
        self.StyleClearAll()
        self.SetSelForeground(True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
        self.SetSelBackground(True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        for i in cont: self.StyleSetSpec(eval('stc.STC_'+i), dump(cont[i]))
        

    def OnUpdateUI(self, event):
        
        
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        
        line = self.GetCurrentLine()
        col = self.GetColumn(caretPos)
        
        # print('update ui, line:', line, 'col:', col, 'pos', caretPos)
        
        word_start = self.WordStartPosition(caretPos, True)
        
        self.word_start = word_start
        self.cur_pos = caretPos
        self.word = self.GetRange(self.word_start, self.cur_pos).strip()
        self.line = line
        self.col = col
        
        # print('word start:', word_start, 'pos:', caretPos, 'word:', self.word)
        # print('cur before:', self.GetCharAt(self.cur_pos-1))
        
        # if (caretPos - word_start >= 3 and col != 0 and not self.autocomp_once and len(self.word)>0):
        #     comps = get_jedi_comp(self.GetValue(), line+1, col)
        #     comps = [ cm for cm in comps if len(cm) > 0 ]
        #     if len(comps) > 0:
        #         print('comps:', comps)
        #         self.AutoCompShow(0, " ".join(comps))
        
        # # inside .        
        # elif (self.GetCharAt(self.cur_pos-1) == 46 or self.GetCharAt(self.cur_pos-2) == 46 or self.GetCharAt(self.cur_pos-3) == 46) and not self.autocomp_once:
        #     comps = get_jedi_comp(self.GetValue(), line+1, col)
        #     comps = [ cm for cm in comps if len(cm) > 0 ]
        #     if len(comps) > 0:
        #         print('comps:', comps)
        #         self.AutoCompShow(0, " ".join(comps))  
        
        #print(caretPos, self.PositionToXY(caretPos), 'updateui')
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # Check before.
        if charBefore and chr(charBefore) in '[]{}()' \
        and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # Check after.
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)
            if charAfter and chr(charAfter) in '[]{}()' \
            and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)     
    
    def OnKeyPressed(self, event):     
        self.last_key = event.GetKeyCode()
        print('press:', self.last_key)
        
        # not tab
        if self.last_key !=9:
            if self.AutoCompActive():
                self.AutoCompCancel()
        
        # press F1
        if self.last_key  == 340:
            docs = get_jedi_doc(self.GetValue(), self.line+1, self.col)
            print('docstring', docs)
            self.CallTipShow(self.cur_pos, docs[0].docstring())
            
        # press ctrl+space
        if self.last_key == 32 and event.ControlDown():
            line = self.line
            col = self.col
            if (self.cur_pos - self.word_start >= 3 and col != 0 and not self.autocomp_once and len(self.word)>0):
                comps = get_jedi_comp(self.GetValue(), line+1, col)
                comps = [ cm for cm in comps if len(cm) > 0 ]
                if len(comps) > 0:
                    print('comps:', comps)
                    self.AutoCompShow(0, " ".join(comps))
            # inside .        
            elif (self.GetCharAt(self.cur_pos-1) == 46 or self.GetCharAt(self.cur_pos-2) == 46 or self.GetCharAt(self.cur_pos-3) == 46) and not self.autocomp_once:
                comps = get_jedi_comp(self.GetValue(), line+1, col)
                comps = [ cm for cm in comps if len(cm) > 0 ]
                if len(comps) > 0:
                    print('comps:', comps)
                    self.AutoCompShow(0, " ".join(comps))  
                    
        self.autocomp_once = 0            
        event.Skip()

    def on_autocomp_finish(self, event):
        # print("comp finished!!")
        self.Remove(self.word_start, self.cur_pos)
        self.autocomp_once = 1


    def set_code(self, code):
        self.code = code
        self.SetValue(code.cont)

    @property
    def object(self): return self.code

    @object.setter
    def object(self, obj): self.set_code(obj)
    

    @property
    def name(self):
        return os.path.split(self.code.name)[-1]

    def Save(self):
        if self.code.saved: return
        if self.code.path is None:
            filt = '|'.join(['%s files (*.%s)|*.%s'%(i.upper(),i,i) for i in 'py'])
            dialog = wx.FileDialog(self, '保存', '', self.code.name, filt, wx.FD_SAVE)
            if dialog.ShowModal() != wx.ID_OK: return dialog.Destroy()
            self.code.path = dialog.GetPath()
            dialog.Destroy()
        self.SaveFile(self.code.path)
        self.code.saved = True

    def OnClose(self, event):
        if not self.code.saved:
            dialog = wx.MessageDialog(self, '关闭前是否保存?', '保存', wx.YES_NO | wx.CANCEL)
            rst = dialog.ShowModal()
            dialog.Destroy()
            if rst == wx.ID_YES: self.Save()
            if not self.code.saved or rst == wx.ID_CANCEL:
                event.Veto()

'''
class A:
    def __init__(self, a, b):
        self.c = a+b

a = A()
a.
'''

if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None)
    CodePad(frame)
    frame.Show()
    app.MainLoop()