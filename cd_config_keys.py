''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github)
Version:
    '0.8.0 2016-05-10'
'''
#! /usr/bin/env python3

import os, json, re, collections, itertools
import  cudatext            as app
from    cudatext        import ed
import  cudax_lib           as apx
from    .cd_plug_lib    import *
from    .cd_keys_report import *

pass;                           LOG     = ( 1==-1)  # Do or dont logging.
pass;                           from pprint import pformat
pass;                           pf=lambda d:pformat(d,width=150)

# I18N
_       = get_translation(__file__)

c9, c10, c13    = chr(9), chr(10), chr(13) 
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
    LST_W, LST_H= sum(COL_WS)+20, 400
    DLG_W, DLG_H= GAP+LST_W+GAP, GAP+LST_H+90+GAP+3
    ccnd_h      = _('Suitable command names will contain all specified words.') \
                +c13+_('Tips:') \
                +c13+_(' · Use "_" for word boundary.') \
                +c13+_('   "_up" selects "upper" but not "group".')
    kcnd_h      = _('Suitable command hotkeys will contain all specified words') \
                +c13+_('Tips:') \
                +c13+_(' · Use "_" for key-name boundary.') \
                +c13+_('   "_f" selects "F1" and "Ctrl+F" but not "Left".')
    addk_h      = _('Set hotkey for command (if no one).'
                  '\rExtend to series hotkeys (if command already has hotkeys).')
    hrpt_h      = _('Shows HTML page with report of all hotkeys in editor.'
                  '\rThe report is usefull to analyze hotkeys in a whole.')
    trpt_h      = _('Show in new tab compact report of hotkeys in editor')
    reND    = re.compile(r'\W')
    def prep_nm(nm):
        nm  = nm.replace('&', '')
        nm  = nm.replace('\\', ': ')
        return nm
    def test_cond(cnd_s, text, text2='', what='cmds'):
        if not cnd_s:       return True
        if not text+text2:  return False
        text    = text + ' ' + text2
        text    = text.upper()
        if '_' in cnd_s:
            text    = '·' + reND.sub('·', text)    + '·'
            cnd_s   = ' ' + cnd_s + ' '
            cnd_s   = cnd_s.replace(' _', ' ·').replace('_ ', '· ')
        pass;                  #LOG and log('cnd_s, text={}',(cnd_s, text))
        return all(map(lambda c:c in text, cnd_s.split()))
#   cmd_id      = 524391
    cmd_id      = ''
    ccnd        = ''
    kcnd        = ''
    focused     = 'ccnd'
    while True:
        ccnd_u  = ccnd.upper()
        kcnd_u  = kcnd.upper()
        fl_NKKIs= [    (prep_nm(nm), k1, k2, id)
                   for (nm,          k1, k2, id)   in nkki_l
                   if  test_cond(ccnd_u, nm)
                   and test_cond(kcnd_u, k1, k2, 'keys')]
        stat    = f(' ({}/{})',len(fl_NKKIs), len(nkki_l)) #if len(fl_NKKIs)==en(nkki_l)
        fl_Is   = [id         for (nm, k1, k2, id) in fl_NKKIs ]
        itms    = (zip([_('Command')+stat, _('Hotkey-1'), _('Hotkey-2')], map(str, COL_WS))
                  ,    [ (nm,                 k1,             k2) for (nm, k1, k2, id) in fl_NKKIs ])
        cnts    =[dict(           tp='lb'   ,tid='ccnd' ,l=GAP          ,w=90   ,cap=_('In &Command:')          ,hint=ccnd_h) # &c
                 ,dict(cid='ccnd',tp='ed'   ,t=GAP      ,l=GAP+90       ,w=150                                              ) #
                 ,dict(           tp='lb'   ,tid='kcnd' ,l=GAP+270      ,w=50   ,cap=_('In &Hotkeys:')          ,hint=kcnd_h) # &h
                 ,dict(cid='kcnd',tp='ed'   ,t=GAP      ,l=GAP+350      ,w=150                                              ) #
                 ,dict(cid='lwks',tp='lvw'  ,t=GAP+30   ,l=GAP          ,w=LST_W,h=LST_H  ,items=itms ,props='1'            ) #     grid
                 ,dict(cid='fltr',tp='bt'   ,tid='ccnd' ,l=GAP+500      ,w=80   ,cap=_('&Filter list'),props='1'            ) # &f  default
                 ,dict(cid='drop',tp='bt'   ,tid='kcnd' ,l=GAP+LST_W-80 ,w=80   ,cap=_('Show &all')                         ) # &a
                 ,dict(cid='add1',tp='bt'   ,t=DLG_H-60 ,l=GAP          ,w=130  ,cap=_('Set/Add Hotkey-&1')     ,hint=addk_h) # &1
                 ,dict(cid='add2',tp='bt'   ,t=DLG_H-30 ,l=GAP          ,w=130  ,cap=_('Set/Add Hotkey-&2')     ,hint=addk_h) # &2
                 ,dict(cid='del1',tp='bt'   ,t=DLG_H-60 ,l=GAP+140      ,w=130  ,cap=_('Remove Hotkey-1 &!')                ) # &!
                 ,dict(cid='del2',tp='bt'   ,t=DLG_H-30 ,l=GAP+140      ,w=130  ,cap=_('Remove Hotkey-2 &@')                ) # &@
                 ,dict(cid='hrpt',tp='bt'   ,t=DLG_H-60 ,l=DLG_W-GAP-200,w=110  ,cap=_('HT&ML-report')          ,hint=hrpt_h) # &m 
                 ,dict(cid='trpt',tp='bt'   ,t=DLG_H-30 ,l=DLG_W-GAP-200,w=110  ,cap=_('&Tab-report')           ,hint=trpt_h) # &t
                 ,dict(cid='help',tp='bt'   ,t=DLG_H-60 ,l=DLG_W-GAP-80 ,w=80   ,cap=_('Hel&p')                             ) # &p 
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
            cmd_nkk[del_i]  = ''
            if  cmd_nkk[2]:
                cmd_nkk[1]  = cmd_nkk[2]
                cmd_nkk[2]  = ''
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
        
        elif btn=='help':
            DW, DH      = DLG_W-2*GAP, DLG_H-2*GAP
            dlg_wrapper(_('Help for "Config Keymaps"'), DLG_W, DLG_H,
                 [dict(cid='htxt',tp='me'    ,t=GAP  ,h=DH-28,l=GAP          ,w=DW   ,props='1,0,1'  ) #  ro,mono,border
                 ,dict(cid='-'   ,tp='bt'    ,t=GAP+DH-23    ,l=GAP+DW-80    ,w=80   ,cap=_('&Close'))
                 ], dict(htxt=
                            _('• In Command.')
                       +c13+ccnd_h
                       +c13+' '
                       +c13+_('• In Hotkeys. ')
                       +c13+kcnd_h
                       +c13+' '
                       +c13+_('• Set/Add. ')
                       +c13+addk_h
                       +c13+' '
                       +c13+_('• HTML-report. ')
                       +c13+hrpt_h
                       +c13+' '
                       +c13+_('• Tab-report. ')
                       +c13+trpt_h
                 ), focus_cid='htxt')
            
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
        if name.endswith(r'\-'):        continue#for n      # command for separator in menu
        if name.startswith('lexer:'):   continue#for n      # ?? lexer? smth-more?
        if name.startswith('plugin:'):  continue#for n      # ?? plugin? smth-more?

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
        if cap.endswith(r'\-'):         continue#for n      # command for separator in menu
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
[+][kv-kv][11dec15] Init
[+][kv-kv][10may16] Shift HK-2 to HK-1 after del HK-1
"""
