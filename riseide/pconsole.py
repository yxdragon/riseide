from code import InteractiveConsole
from multiprocessing import Pipe, Process
import threading, time
from pdb import Pdb

def pretty_str(obj, l=10):
    if isinstance(obj, int):
        return str(obj)
    elif isinstance(obj, float):
        return str(obj)
    elif isinstance(obj, str):
        if len(obj)<=l: return obj
        return obj[:l//2] + ' ... ' + obj[-l//2:]
    elif type(obj) in (tuple, list):
        length = len(obj)
        if len(obj)>l: obj = obj[:l//2] + obj[-l//2:]
        tps = set([type(i) for i in obj])
        if set(tps).issubset({int, float}):
            if length>l:
                s = '%s%s'%(obj[:l//2], obj[-l//2:])
                return s.replace('][', ' ... ')
            return str(obj)
        else: return f'length [{length}]'
    elif isinstance(obj, np.ndarray):
        return '%s array in %s'%(obj.dtype, obj.shape)
    elif isinstance(obj, pd.DataFrame):
        return 'dataframe in %s'%(obj.shape,)
    else: return 'object'

def get_locals(var=None, filt=['all']):
    var = var or locals()
    cont = []
    for key in var.keys():
        if not 'all' in filt and type(var[key]) not in filt: continue
        cont.append((key, str(type(var[key])), pretty_str(var[key])))
    return cont

class Powerdb(Pdb):
    def precmd(self, line):
        if not isinstance(line, str): return line
        return super().precmd(line)

    def onecmd(self, line):
        self.prompt = '--> '
        if line==':r':
            self.message('%-15s'%'[Step Out....]')
            return self.do_return(None)
        if line==':s':
            self.message('%-15s'%'[Step Into...]')
            return self.do_step(None)
        if line==':n':
            self.message('%-15s'%'[Step Next...]')
            return self.do_next(None)
        if line==':c':
            self.message('%-15s'%'[Continue....]')
            return self.do_continue(None)
        if line==':u':
            return self.do_up(None)
        if line==':d':
            return self.do_down(None)
        if line==':l':
            return self.do_list(None)
        if line==':w':
            return self.do_where(None)
        if line==':q':
            self.message('%-15s'%'[Step Debug..]')
            return self.do_quit(None)
        if line==':m':
            return self.refresh_bpmark(None)
        if isinstance(line, tuple):
            method, name = line
            if method=='locals':
                self.message((get_locals(self.curframe_locals, name), True))
                self.prompt = None
            if method=='breakpoint':
                self.clear_all_breaks()
                for file, line in name:
                    self.set_break(file, line)
                self.message(('breakpoint', True))
                if self.first: 
                    self.first, self.prompt = False, None
                    return
                self.message('%-15s'%'[Set BreakPoint...]\n')
            return 0
        _, self.message = self.message, print
        self.default(line)
        self.message = _

    def user_call(self, frame, argument_list):
        if self._wait_for_mainpyfile: return
        if self.stop_here(frame):
            self.interaction(frame, None)

    def user_return(self, frame, return_value): pass

    def print_stack_entry(self, frame_lineno, prompt_prefix=''):
        frame, lineno = frame_lineno
        import linecache
        filename = self.canonic(frame.f_code.co_filename)
        line = linecache.getline(filename, lineno, frame.f_globals)
        {'path':filename, 'no':lineno, 'line':line}
        self.message(({'path':filename, 'no':lineno, 'line':line.rstrip()}, True))
        if self.first: self.message('--> %-15s'%'[Debugging...]')
        self.message('%-15s ln:%-4d || %s'%(
                filename.split('\\')[-1], lineno, line))

    def debug(self, filename, globals=None, locals=None):
        self.prompt, self.first = '--> ', True
        import __main__
        __main__.__dict__.clear()
        __main__.__dict__.update({"__name__"    : "__main__",
            "__file__"    : filename, "__builtins__": __builtins__, })
        self._wait_for_mainpyfile = True
        self.mainpyfile = self.canonic(filename)
        self._user_requested_quit = False
        with open(filename, "rb") as fp:
            statement = "exec(compile(%r, %r, 'exec'))" % (fp.read(), self.mainpyfile)
        self.run(statement, globals, locals)
        self.message(({'path':'end', 'no':0, 'line':''}, False))
        self.message('Debug Completed...\n')

class Console(InteractiveConsole):
    def __init__(self, conn, locals=None, filename="<console>"):
        super().__init__(locals, filename)
        self.buf = []
        self.pipe = conn
        td = threading.Thread(target=self.listening, args=(), daemon=True)
        td.start()
        __builtins__['input'] = self.input
           
    def listening(self):
        while True:
            self.buf.append(self.pipe.recv())

    def write(self, data, end='\n'):
        #if isinstance(data, str): data += end
        self.pipe.send(data)

    def mplpause(self, interval):
        from matplotlib import _pylab_helpers
        manager = _pylab_helpers.Gcf.get_active()
        if manager is not None:
            canvas = manager.canvas
            if canvas.figure.stale:
                canvas.draw_idle()
            try:
                canvas.start_event_loop(interval)
            except: time.sleep(interval)
        else: time.sleep(interval)

    def execfile(self, path):
        with open(path) as f: exec(f.read(), self.locals)

    def debug(self, path):
        db = Powerdb()
        #f = lambda x: x+'\n' if isinstance(x, str) else x
        #db.message = lambda x: self.write(f(x))
        db.message = self.write
        db.debug(path, locals=self.locals)

    def input(self, prompt=None):
        if not prompt is None: self.pipe.send(prompt)
        while True:
            if len(self.buf)>0: return self.buf.pop(0)
            self.mplpause(0.1)

    def raw_input(self, prompt=""):
        line = self.input(prompt)
        if isinstance(line, str): return line

        method, name = line
        if '(' in name: 
            self.pipe.send(('cannot deduce', False)); 
        elif method=='dir': # list field
            try: 
                value = eval('dir(%s)'%name, None, self.locals)
                self.pipe.send((value, True))
            except: self.pipe.send((sys.exc_info()[1], False))
        elif method=='get': # send binary object
            try: self.pipe.send((eval(name, None, self.locals), True))
            except: self.pipe.send((sys.exc_info()[1], False))
        elif method == 'set': # write binary object
            try: 
                exec('%s = %s'%name, self.locals)
                self.pipe.send(('%s = %s'%name, True))
            except: self.pipe.send((sys.exc_info()[1], False))
        elif method == 'doc': # dot means document
            try: 
                value = eval(name+'.__doc__', None, self.locals)
                self.pipe.send((value, True))
            except: self.pipe.send((sys.exc_info()[1], False))
        elif method == 'locals':
            try: self.pipe.send((get_locals(self.locals, name), True))
            except: self.pipe.send((sys.exc_info()[1], False))
        return self.raw_input()

def interact(conn):
    import sys, time, threading
    import matplotlib
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    plt.ion()
    conn.write = conn.send
    conn.read = conn.recv
    sys.stdout = conn

    
          
    cs = Console(conn, {'plt':plt, 'pipe':conn})
    cs.locals['execfile'] = cs.execfile
    cs.locals['debug'] = cs.debug
    cs.interact()

    #threading.Thread(target=cs.interact, args=())
    #time.sleep(100)
          
class ProcessConsole:
    def __init__(self): 
        self.status = 'nothing'

    def listening(self):
        while True:
            line = self.pin.recv()
            if isinstance(line, str):
                self.recv(line)
                if line=='>>> ': self.ready()
                if line=='... ': self.goon()
            elif self.status=='waiting':
                self.status = line
    
    def terminate(self):
        self.process.terminate()
        self.recv = self.ready = self.goon = self.wait = None

    def write(self, data):
        self.wait()
        self.pin.send(data)

    def getobj(self, method, name):
        self.pin.send((method, name))
        self.status = 'waiting'
        while self.status=='waiting': time.sleep(0.01)
        rst, self.status = self.status, 'nothing'
        return rst

    def debug(self, method, name):
        if method == 'action':
            self.pin.send(name)
        if method == 'breakpoint':
            self.pin.send((method, name))
        self.status = 'waiting'
        while self.status=='waiting': time.sleep(0.01)
        rst, self.status = self.status, 'nothing'
        if method == 'action':
            pass #self.recv('[Debug Completed...]\n')
        return rst

    def start(self, recv=print, ready=None, goon=None, wait=None):
        nf = lambda p=None: p 
        self.recv, self.ready = recv, ready or nf
        self.goon, self.wait =  goon or nf, wait or nf
        self.pout, self.pin = Pipe()
        self.process = Process(target=interact, args=(self.pout,), daemon=True)
        self.thread = threading.Thread(target=self.listening, args=(), daemon=True)
        self.thread.start(), self.process.start()

if __name__ == '__main__':
    a = InteractiveConsole()
    a.runsource
