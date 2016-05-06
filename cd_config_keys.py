''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github)
Version:
    '0.1.0 2016-05-06'
'''
#! /usr/bin/env python3

import os, json, re, collections, itertools
import  cudatext            as app
from    cudatext        import ed
import  cudax_lib           as apx
from    .cd_plug_lib    import *
from    .cd_keys_report import *

pass;                           LOG     = (-1==-1)  # Do or dont logging.
pass;                           from pprint import pformat
pass;                           pf=lambda d:pformat(d,width=150)

# I18N
_       = get_translation(__file__)

GAP     = 5

class Command:    
    def dlg_config_keys(self):
        if app.app_api_version()<'1.0.136':     # dlg_hotkey, PROC_GET_HOTKEY, PROC_SET_HOTKEY
            return app.msg_status(_('Need update CudaText'))
        dlg_config_keys()
       #def dlg_config_keys

def dlg_config_keys():
    def prep_keys_info():
        cmdCNKKIs   = collect_keys()
        pass;                  #LOG and log('cmdCNKKIs={}',pf(cmdCNKKIs))
        pass;                  #LOG and open(r'py\cuda_config_keys\t.log', 'w').write(pf(cmdCNKKIs))
        pass;                  #return
        nkki_l      =  [(nm,k1,k2,id)   for (ch,nm,k1,k2,id) in cmdCNKKIs]
        id2nkks     =  {id:[nm,k1,k2]   for (ch,nm,k1,k2,id) in cmdCNKKIs}
        ks2id       =  {k1:id           for (ch,nm,k1,k2,id) in cmdCNKKIs}
        ks2id.update(  {k2:id           for (ch,nm,k1,k2,id) in cmdCNKKIs})
        return nkki_l, id2nkks, ks2id
       #def prep_keys_info
    nkki_l, id2nkks, ks2id = prep_keys_info()
        
    COL_WS      = [340, 150, 150] 
    LST_W, LST_H= sum(COL_WS)+20, 600
    DLG_W, DLG_H= GAP+LST_W+GAP, GAP+LST_H+90+GAP+3
    ccnd_h      = _('Suitable command names contain all specified words')
    kcnd_h      = _('Suitable command hotkeys contain all specified words')
    addk_h      = _('Set hotkey for command (if no one).'
                  '\rExtend to series hotkeys (if command already has hotkeys).'
                    )
    hrpt_h      = _('Shows HTML page with report of all hotkeys in editor.'
                  '\rThe report is usefull to analyze hotkeys in a whole.'
                    )
    trpt_h      = _('Show in new tab compact report of hotkeys in editor'
                    )

#   cmd_id      = 524391
    cmd_id      = ''
    ccnd        = ''
    kcnd        = ''
#   lwks_n      = 0
    focused     = 'ccnd'
    while True:
        fl_NKKIs= [    (nm, k1, k2, id)
                   for (nm, k1, k2, id)   in nkki_l
                   if  all(map(lambda c:c in      nm.upper(), ccnd.upper().split()))
                   and all(map(lambda c:c in (k1+k2).upper(), kcnd.upper().split()))]
        fl_Is   = [id         for (nm, k1, k2, id) in fl_NKKIs ]
        itms    = (zip([_('Command'), _('Hotkey 1'), _('Hotkey 2')], map(str, COL_WS))
                  ,    [ (nm,           k1,             k2) for (nm, k1, k2, id) in fl_NKKIs ])
        cnts    =[dict(           tp='lb'   ,tid='ccnd' ,l=GAP          ,w=90   ,cap=_('In Co&mmand:')          ,hint=ccnd_h) # &m
                 ,dict(cid='ccnd',tp='ed'   ,t=GAP      ,l=GAP+90       ,w=150                                              ) #
                 ,dict(           tp='lb'   ,tid='kcnd' ,l=GAP+270      ,w=50   ,cap=_('In Hot&keys:')          ,hint=kcnd_h) # &k
                 ,dict(cid='kcnd',tp='ed'   ,t=GAP      ,l=GAP+350      ,w=150                                              ) #
                 ,dict(cid='lwks',tp='lvw'  ,t=GAP+30   ,l=GAP          ,w=LST_W,h=LST_H  ,items=itms ,props='1'            ) #     grid
                 ,dict(cid='fltr',tp='bt'   ,tid='ccnd' ,l=GAP+500      ,w=80   ,cap=_('&Filter list'),props='1'            ) # &f  default
                 ,dict(cid='drop',tp='bt'   ,tid='kcnd' ,l=GAP+LST_W-80 ,w=80   ,cap=_('Sho&w all')                         ) # &w
                 ,dict(cid='add1',tp='bt'   ,t=DLG_H-60 ,l=GAP          ,w=130  ,cap=_('Set/Add hotkey &1')         ,hint=addk_h) # &1
                 ,dict(cid='add2',tp='bt'   ,t=DLG_H-30 ,l=GAP          ,w=130  ,cap=_('Set/Add hotkey &2')         ,hint=addk_h) # &2
                 ,dict(cid='del1',tp='bt'   ,t=DLG_H-60 ,l=GAP+140      ,w=130  ,cap=_('Remove hotke&y 1')                  ) # &r
                 ,dict(cid='del2',tp='bt'   ,t=DLG_H-30 ,l=GAP+140      ,w=130  ,cap=_('Remove ho&tkey 2')                  ) # &o
                 ,dict(cid='hrpt',tp='bt'   ,t=DLG_H-60 ,l=DLG_W-GAP-200,w=110  ,cap=_('&Html-report')          ,hint=hrpt_h) # &h 
                 ,dict(cid='trpt',tp='bt'   ,t=DLG_H-30 ,l=DLG_W-GAP-200,w=110  ,cap=_('&Tab-report')           ,hint=trpt_h) # &t
                 ,dict(cid='help',tp='bt'   ,t=DLG_H-60 ,l=DLG_W-GAP-80 ,w=80   ,cap=_('Help')                              ) #  
                 ,dict(cid='-'   ,tp='bt'   ,t=DLG_H-30 ,l=DLG_W-GAP-80 ,w=80   ,cap=_('Close')                             ) #  
                ]
        lwks_n  = -1    if 0==len(fl_Is)        else \
                   0    if cmd_id not in fl_Is  else \
                   fl_Is.index(cmd_id)
        pass;                   LOG and log('lwks_n={}',(lwks_n))
        vals    = dict(ccnd=ccnd
                      ,kcnd=kcnd
                      ,lwks=lwks_n)
        pass;                  #LOG and log('in-vals={}',(vals))
        btn, vals, chds = dlg_wrapper(_('Keymap'), DLG_W, DLG_H, cnts, vals, focus_cid=focused)
        pass;                  #LOG and log('an-vals={}',(vals))
        pass;                  #LOG and log('chds={}',(chds))
        if btn is None or btn=='-':    return#while True
        ccnd    = vals['ccnd'].strip()
        kcnd    = vals['kcnd'].strip()
        lwks_n  = vals['lwks']
        cmd_id  = '' if lwks_n==-1 else fl_Is[lwks_n]
        pass;                   LOG and log('cmd_id={}',(cmd_id,))
        focused = chds[0] if 1==len(chds) else focused
        pass;                   LOG and log('chds, focused={}',(chds, focused))
        if False:pass
#       elif btn in 'fltr':
#           focused = chds[0] if 1==len(chds) else 'ccnd'
        elif btn=='drop':
            ccnd    = ''
            kcnd    = ''
        
        elif btn=='trpt':
            # Compact report to tab
            app.file_open('')
            ed.set_text_all(get_str_report())
        elif btn=='hrpt':
            # Full report to HTML
            htm_file = os.path.join(tempfile.gettempdir(), '{}_keymapping.html'.format(app_name))
            do_report(htm_file)
            webbrowser.open_new_tab('file://'+htm_file)
            app.msg_status(_('Opened browser with file ')+htm_file)
        
        elif btn in ('del1', 'del2') and cmd_id:
            # Delete the hotkeys
            cmd_nkk = id2nkks[cmd_id]
            del_i   = 1 if btn=='del1' else 2
            if not cmd_nkk[del_i]:  continue#while
            cmd_nkk[del_i]    = ''
            set_ok  = app.app_proc(app.PROC_SET_HOTKEY, f('{}|{}|{}', cmd_id, cmd_nkk[1], cmd_nkk[2]))
            if not set_ok:  log('Fail to use PROC_SET_HOTKEY for cmd "{}"', cmd_id)
            nkki_l, id2nkks, ks2id = prep_keys_info()
        
        elif btn in ('add1', 'add2') and cmd_id:
            ext_k   = app.dlg_hotkey()
            pass;               LOG and log('ext_k={}',(ext_k,))
            if ext_k is None:   continue#while
            cmd_nkk = id2nkks[cmd_id]
            add_i   = 1 if btn=='add1' else 2
            old_k   = cmd_nkk[add_i]
            new_k   = old_k + ' * ' + ext_k if old_k else ext_k
            pass;               LOG and log('cmd_nkk,old_k,new_k={}',(cmd_nkk,old_k,new_k))
            if new_k in ks2id:
                dbl_id  = ks2id[new_k]
                dbl_nkk = id2nkks[dbl_id]
                if app.msg_box(f(_('Hotkey "{}" is already assigned \nto command "{}".\n\nDo you want to reassign the hotkey \nto selected command "{}"?')
                                , new_k, dbl_nkk[0], cmd_nkk[0]), app.MB_OKCANCEL)==app.ID_CANCEL: continue#while
                dbl_i   = 1 if dbl_nkk[1]==new_k else 2
                pass;           LOG and log('dbl_id, dbl_nkk={}',(dbl_id, dbl_nkk))
                dbl_nkk[dbl_i]  = ''
                if dbl_nkk[2]:
                    dbl_nkk[1], dbl_nkk[2] = dbl_nkk[2], ''
                pass;           LOG and log('dbl_id, dbl_nkk={}',(dbl_id, dbl_nkk))
                set_ok  = app.app_proc(app.PROC_SET_HOTKEY, f('{}|{}|{}', dbl_id, dbl_nkk[1], dbl_nkk[2]))
                if not set_ok:  log('Fail to use PROC_SET_HOTKEY for cmd "{}"', dbl_id)

            cmd_nkk[add_i]  = new_k
            pass;               LOG and log('cmd_id, cmd_nkk={}',(cmd_id, cmd_nkk))
            set_ok  = app.app_proc(app.PROC_SET_HOTKEY, f('{}|{}|{}', cmd_id, cmd_nkk[1], cmd_nkk[2]))
            if not set_ok:  log('Fail to use PROC_SET_HOTKEY for cmd "{}"', cmd_id)
            nkki_l, id2nkks, ks2id = prep_keys_info()
        
       #while True
    app.msg_status('OK')
   #def dlg_config_keys

def collect_keys():
    keys_json   = os.path.join(app.app_path(app.APP_DIR_SETTINGS), 'keys.json')
    keys        = apx._json_loads(open(keys_json).read())

    cmdinfos    = []
    # Core cmds
    pass;                      #LOG and open(r'py\cuda_config_keys\t.log', 'w')
    for n in itertools.count():
        # 5      ,'smth', 'Shift+Ctrl+F1', 'Alt+Q * Ctrl+T'
        cmdinfo = app.app_proc(app.PROC_GET_COMMAND, str(n))
        if cmdinfo is None:             break       #for n
        if cmdinfo[0]<=0:               continue    #for n
        # Add default category
        cmdinfo = ('Commands', cmdinfo[1], cmdinfo[2], cmdinfo[3], cmdinfo[0])

        ctg, name, keys1, keys2, cid = cmdinfo
        if name.startswith('lexer:'):   continue    #for n      # ?? lexer? smth-more?
        if name.startswith('plugin:'):  continue    #for n      # ?? plugin? smth-more?

        pass;                  #LOG and open(r'py\cuda_config_keys\t.log', 'a').write(pf(('cmd', n, cmdinfo))+'\n')
        cmdinfos += [cmdinfo]
       #for n
    
    # Plugin cmds
    for n in itertools.count():
        if not    app.app_proc(app.PROC_GET_COMMAND_PLUGIN, str(n)): break#for n
        (cap
        ,modul
        ,meth
        ,par
        ,lxrs)  = app.app_proc(app.PROC_GET_COMMAND_PLUGIN, str(n))
        pass;                  #LOG and open(r'py\cuda_config_keys\t.log', 'a').write(pf(('plg', n, (cap,modul,meth,par,lxrs)))+'\n')
        plug_id = modul+','+meth+(','+par if par else '')
        dct_keys= keys.get(plug_id, {})
        
        cmdinfos += [('Plugins'
                    , 'plugin: '+cap
                    , ' * '.join(dct_keys.get('s1', []))
                    , ' * '.join(dct_keys.get('s2', []))
                    , f('{},{},{}', modul, meth, par).rstrip(',')
                    )]
       #for n
    return cmdinfos
   #def collect_keys

#######################################################
if __name__ == '__main__':
    pass;                       print('OK')

""" TODO
[ ][kv-kv][11dec15] ?
"""
