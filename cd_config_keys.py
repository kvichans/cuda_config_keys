''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github)
Version:
    '1.1.3 2018-02-19'
'''
#! /usr/bin/env python3

import os, json, re, collections, itertools
from    fnmatch         import fnmatch
import  cudatext            as app
import  cudatext_cmd        as cmds
from    cudatext        import ed
import  cudax_lib           as apx
from    .cd_plug_lib    import *
from    .cd_keys_report import *

pass;                           LOG     = (-1==-1)  # Do or dont logging.
pass;                           from pprint import pformat
pass;                           pf=lambda d:pformat(d,width=150)

# I18N
_       = get_translation(__file__)

c9, c10, c13    = chr(9), chr(10), chr(13) 
GAP     = 5

sndt        = None
try:    # Is plugin cuda_snip2call acitive?
    from cuda_snip2call import SnipData
    sndt    = SnipData()
except ImportError as ex:
    pass;                       LOG and log('ex={}',(ex))
    pass
#sndt        = None

class Command:    
    def dlg_config_keys(self):
#       if app.app_api_version()<'1.0.136':     # dlg_hotkey, PROC_GET_HOTKEY, PROC_SET_HOTKEY
        if app.app_api_version()<'1.0.212':     # depr PROC_GET_COMMAND, PROC_GET_COMMAND_PLUGIN
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
    pass;                      #LOG and log('nkki_l={}',(pf(nkki_l)))
        
    COL_WS      = [340, 200, 200, 150] 
    COL_WS      = [COL_WS[0]+COL_WS[3]]+COL_WS[1:3]+[0] if not sndt else COL_WS
    LST_W, LST_H= sum(COL_WS)+20, 400-5
    DLG_W, DLG_H= 5+LST_W+5+100+5, 5+LST_H+105+5+3
    lfk1        = 5+COL_WS[0]+5
    lfk2        = 5+COL_WS[0]+COL_WS[1]+5
    lfsn        = 5+COL_WS[0]+COL_WS[1]+COL_WS[2]+5
    lrpt        = DLG_W-5-100
    ccnd_h      = _('Suitable command names will contain all specified words.') \
                +c13+_('Tips:') \
                +c13+_(' · Use "_" for word boundary.') \
                +c13+_('   "_up" selects "upper" but not "group".')
    kcnd_h      = _('Suitable command hotkeys will contain all specified words.') \
                +c13+_('Tips:') \
                +c13+_(' · Use "_" for key-name boundary.') \
                +c13+_('   "_f" selects "F1" and "Ctrl+F" but not "Left".')
    scnd_h      = _('Suitable command snips will match specified string.') \
                +c13+_('Usage:') \
                +c13+_(' · Type "/" and snip string and push Tab-key.') \
                +c13+_('Tips:') \
                +c13+_(' · Use ? for any character and * for any fragment.')
    addk_h      = _('Set hotkey for command (if no one).'
                  '\rExtend to series hotkeys (if command already has hotkeys).')
    hrpt_h      = _('Shows HTML page with report of all hotkeys in editor.'
                  '\rThe report is usefull to analyze hotkeys in a whole.')
    trpt_h      = _('Show compact report of hotkeys in new tab.'
                  '\rThe report is usefull to find free hotkeys.')
    cpnm_h      = _('Copy command name to clipboard')
    open_h      = _('Open source of plugin code')
    reND    = re.compile(r'\W')
    def is_cond4snps(cond, sns_l):
        if not cond:    return  True
        if not sns_l:   return  False
        return any(map(lambda sn:fnmatch(sn, cond), sns_l))
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
    def bmix(bor12, bor23, val1, val2, val3):
        val12   = val1  or val2     if bor12 else        val1  and val2
        return    val12 or val3     if bor23 else        val12 and val3
#   cmd_id      = 524391
    cmd_id      = ''
    ccnd        = ''
    kcnd        = ''
    scnd        = ''
    orcn        = False
    orsn        = False
    focused     = 'ccnd'
    while True:
        ccnd_u  = ccnd.upper()
        kcnd_u  = kcnd.upper()
        pass;                  #LOG and log('ccnd_u, kcnd_u, scnd={}',(ccnd_u, kcnd_u, scnd))
        nkkis_l = [    (nm, k1, k2, id, sndt.get_snips(id) if sndt else [])
                   for (nm, k1, k2, id)   in nkki_l]
        pass;                  #LOG and log('nkkis_l={}',(pf(nkkis_l)))
        fl_NKKISs=[    (nm, k1, k2, id, sns)
                   for (nm, k1, k2, id, sns)   in nkkis_l
                   if  bmix(orcn, orsn
                                  ,(not ccnd_u or               test_cond(ccnd_u, nm))
                                  ,(not kcnd_u or               test_cond(kcnd_u, k1, k2, 'keys'))
                                  ,(not scnd   or not sndt   or is_cond4snps(scnd, sns)) )]
        stat    = f(' ({}/{})',len(fl_NKKISs), len(nkkis_l))
        fl_Is   = [id         for (nm, k1, k2, id, sn) in fl_NKKISs ]   ##!!
        itms    = (zip([_('Command')+stat, _('Hotkey-1'), _('Hotkey-2'), _('Snip')], map(str, COL_WS))
                  ,    [ (nm,                 k1,             k2,          ', '.join(sns)) 
                        for  (nm, k1, k2, id, sns) in fl_NKKISs ])
        cnts    =([]
                 +[dict(cid='fltr',tp='bt'  ,t=5+40+10  ,l=lrpt ,w=100  ,cap=_('&Filter')       ,props='1'          )] # &f  default
                 +[dict(cid='drop',tp='bt'  ,t=5+70+10  ,l=lrpt ,w=100  ,cap=_('&All')                              )] # &a
                 +[dict(cid='orcn',tp='ch'  ,t=5        ,l=lfk1-50,w=40 ,cap=_('&OR')           ,act='1'            )] # &o
                +([] if not sndt else []
                 +[dict(cid='orsn',tp='ch'  ,t=5        ,l=lfsn-50,w=40 ,cap=_('O&R')           ,act='1'            )] # &r
                )
                 +[dict(           tp='lb'  ,tid='orcn' ,l=5+5  ,w=90   ,cap=_('In &Command:')          ,hint=ccnd_h)] # &c
                 +[dict(cid='ccnd',tp='ed'  ,t=5+20     ,l=5+5  ,w=150                                              )] #
                 +[dict(           tp='lb'  ,tid='orcn' ,l=lfk1 ,w=50   ,cap=_('In &Hotkeys:')          ,hint=kcnd_h)] # &h
                 +[dict(cid='kcnd',tp='ed'  ,t=5+20     ,l=lfk1 ,w=120                                              )] #
                +([] if not sndt else []
                 +[dict(           tp='lb'  ,tid='orsn' ,l=lfsn ,w=50   ,cap=_('In &Snip(s):')          ,hint=scnd_h)] # &s
                 +[dict(cid='shlp',tp='bt'  ,tid='orsn' ,l=lfsn+80,w=20 ,cap=_('&?')                                )] # &?
                 +[dict(cid='scnd',tp='ed'  ,t=5+20     ,l=lfsn ,w=100                                              )] #
                )
                 +[dict(cid='lwks',tp='lvw' ,t=5+50     ,l=5    ,w=LST_W,h=LST_H  ,items=itms   ,props='1'          )] #     grid
                
                 +[dict(cid='cpnm',tp='bt'  ,t=DLG_H-60 ,l=5+5  ,w=110  ,cap=_('Copy &name')            ,hint=cpnm_h)] # &n
                +([] if not apx.get_opt('config_keys_with_open', False) else []
                 +[dict(cid='open',tp='bt'  ,t=DLG_H-30 ,l=5+5  ,w=110  ,cap=_('Open code &#')          ,hint=open_h)] # &#
                )
                 +[dict(cid='hrpt',tp='bt'  ,t=DLG_H-60 ,l=130  ,w=150  ,cap=_('Report to HT&ML')       ,hint=hrpt_h)] # &m
                 +[dict(cid='trpt',tp='bt'  ,t=DLG_H-30 ,l=130  ,w=150  ,cap=_('Report to &Tab')        ,hint=trpt_h)] # &t
                 +[dict(cid='add1',tp='bt'  ,t=DLG_H-60 ,l=lfk1 ,w=150  ,cap=_('Set/Add Hotkey-&1')     ,hint=addk_h)] # &1
                 +[dict(cid='del1',tp='bt'  ,t=DLG_H-30 ,l=lfk1 ,w=150  ,cap=_('Remove Hotkey-1 &!')                )] # &!
                 +[dict(cid='add2',tp='bt'  ,t=DLG_H-60 ,l=lfk2 ,w=150  ,cap=_('Set/Add Hotkey-&2')     ,hint=addk_h)] # &2
                 +[dict(cid='del2',tp='bt'  ,t=DLG_H-30 ,l=lfk2 ,w=150  ,cap=_('Remove Hotkey-2 &@')                )] # &@
                +([] if not sndt else []
                 +[dict(cid='asnp',tp='bt'  ,t=DLG_H-60 ,l=lfsn ,w=150  ,cap=_('Set/A&dd Snip')                     )] # &d
                 +[dict(cid='rsnp',tp='bt'  ,t=DLG_H-30 ,l=lfsn ,w=150  ,cap=_('R&emove Snip(s)')                   )] # &e
                )
#                +[dict(cid='hrpt',tp='bt'  ,t=DLG_H-120,l=lrpt ,w=100  ,cap=_('In HT&ML')              ,hint=hrpt_h)] # &m 
#                +[dict(cid='trpt',tp='bt'  ,t=DLG_H-90 ,l=lrpt ,w=100  ,cap=_('In &Tab')               ,hint=trpt_h)] # &t
                 +[dict(cid='help',tp='bt'  ,t=DLG_H-60 ,l=lrpt ,w=100  ,cap=_('Hel&p')                             )] # &p 
                 +[dict(cid='-'   ,tp='bt'  ,t=DLG_H-30 ,l=lrpt ,w=100  ,cap=_('Close')                             )] #  
                )
        lwks_n  = -1    if 0==len(fl_Is)        else \
                   0    if cmd_id not in fl_Is  else \
                   fl_Is.index(cmd_id)
        pass;                  #LOG and log('lwks_n={}',(lwks_n))
        vals    =       dict(ccnd=ccnd
                            ,kcnd=kcnd
                            ,orcn=orcn
                            ,lwks=lwks_n)
        if sndt:
            vals.update(dict(scnd=scnd
                            ,orsn=orsn
            ))
        pass;                  #LOG and log('in-vals={}',(vals))
        btn, vals, chds = dlg_wrapper(_('Config Hotkeys'), DLG_W, DLG_H, cnts, vals, focus_cid=focused)
        pass;                  #LOG and log('an-vals={}',(vals))
        pass;                  #LOG and log('chds={}',(chds))
        if btn is None or btn=='-':    return#while True
        ccnd    = vals['ccnd'].strip()
        kcnd    = vals['kcnd'].strip()
        scnd    = vals['scnd'].strip()  if sndt else ''
        orcn    = vals['orcn']
        orsn    = vals['orsn']          if sndt else False
        lwks_n  = vals['lwks']
        cmd_id  = '' if lwks_n==-1 else fl_Is[lwks_n]
        pass;                  #LOG and log('cmd_id={}',(cmd_id,))
        focused = chds[0] if 1==len(chds) else focused
        pass;                  #LOG and log('chds, focused={}',(chds, focused))
        if False:pass
        elif btn in 'fltr':
            focused = 'lwks'
        elif btn=='drop':
            ccnd    = ''
            kcnd    = ''
            scnd    = ''
        
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
        
        elif btn=='open' and cmd_id:
            pass;               LOG and log('cmd_id={}',(cmd_id))
            if type(cmd_id)!=str:   continue#while
            plug_mdl,   \
            plug_mth    = cmd_id.split(',')[0:2]
            plug_mth    = 'def '+ plug_mth + '(self):'
            plug_dir    = app.app_path(app.APP_DIR_PY)+os.sep+plug_mdl
            plug_py     = plug_dir+os.sep+'__init__.py'
            plug_body   = open(plug_py, encoding='UTF-8').read()
            pass;               LOG and log('plug_mdl,plug_mth,plug_dir,plug_py={}',(plug_mdl,plug_mth,plug_dir,plug_py))
            mch         = re.search(r'from\s+\.(\w+)\s+import\s+Command', plug_body)
            if mch:
                # from .other_py import Command
                plug_py = plug_dir+os.sep+mch.group(1)+'.py'
                pass;           LOG and log('plug_py={}',(plug_py))
                plug_body=open(plug_py, encoding='UTF-8').read()
            if plug_mth not in plug_body:   continue#while
            # Open
            app.file_open(plug_py)
            # Locate
            user_opt= app.app_proc(app.PROC_GET_FIND_OPTIONS, '')
            ed.cmd(cmds.cmd_FinderAction, chr(1).join([]
                +['findnext']
                +[plug_mth]
                +['']
                +['fa']
            ))
            app.app_proc(app.PROC_SET_FIND_OPTIONS, user_opt)
            break#while
        
        elif btn=='cpnm' and cmd_id:
            cmd_nkk = id2nkks[cmd_id]
            app.app_proc(app.PROC_SET_CLIP, cmd_nkk[0])
        
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
            pass;              #LOG and log('ext_k={}',(ext_k,))
            if ext_k is None:   continue#while
            cmd_nkk = id2nkks[cmd_id]
            add_i   = 1 if btn=='add1' else 2
            old_k   = cmd_nkk[add_i]
            new_k   = old_k + ' * ' + ext_k if old_k else ext_k
            pass;              #LOG and log('cmd_nkk,old_k,new_k={}',(cmd_nkk,old_k,new_k))
            if new_k in ks2id:
                dbl_id  = ks2id[new_k]
                dbl_nkk = id2nkks[dbl_id]
                if app.msg_box(f(_('Hotkey "{}" is already assigned '
                                   '\nto command "{}".'
                                   '\n'
                                   '\nDo you want to reassign the hotkey '
                                   '\nto selected command "{}"?')
                                , new_k, dbl_nkk[0], cmd_nkk[0]), app.MB_OKCANCEL)==app.ID_CANCEL: continue#while
                dbl_i   = 1 if dbl_nkk[1]==new_k else 2
                pass;          #LOG and log('dbl_id, dbl_nkk={}',(dbl_id, dbl_nkk))
                dbl_nkk[dbl_i]  = ''
                if dbl_nkk[2]:
                    dbl_nkk[1], dbl_nkk[2] = dbl_nkk[2], ''
                pass;          #LOG and log('dbl_id, dbl_nkk={}',(dbl_id, dbl_nkk))
                set_ok  = app.app_proc(app.PROC_SET_HOTKEY, f('{}|{}|{}', dbl_id, dbl_nkk[1], dbl_nkk[2]))
                if not set_ok:  log('Fail to use PROC_SET_HOTKEY for cmd "{}"', dbl_id)

            cmd_nkk[add_i]  = new_k
            pass;              #LOG and log('cmd_id, cmd_nkk={}',(cmd_id, cmd_nkk))
            set_ok  = app.app_proc(app.PROC_SET_HOTKEY, f('{}|{}|{}', cmd_id, cmd_nkk[1], cmd_nkk[2]))
            if not set_ok:  log('Fail to use PROC_SET_HOTKEY for cmd "{}"', cmd_id)
            nkki_l, id2nkks, ks2id = prep_keys_info()
        
        elif btn=='rsnp' and cmd_id and sndt: 
            cnm     = sndt.get_name(cmd_id)
            snp_l   = sndt.get_snips(cmd_id)
            snps    = ', '.join(snp_l)
            if app.msg_box(f(_('Do you want to remove snip(s) '
                               '\n    {}'
                               '\nfor command "{}"?')
                            , snps, cnm), app.MB_OKCANCEL)==app.ID_CANCEL: continue#while
            for snp in snp_l:
                sndt.free(snp)
                
        elif btn=='shlp'            and sndt:
            app.msg_box(sndt.snip_help, app.MB_OK)

        elif btn=='asnp' and cmd_id and sndt:
            cnm     = sndt.get_name(cmd_id)
            new_sn  = app.dlg_input(f(_('Add snip for "{}"'), cnm), '') 
            if not new_sn:  continue#while
            while not SnipData.is_snip(new_sn):
                app.msg_status(SnipData.msg_correct_snip)
                new_sn  = app.dlg_input(f(_('Snip for "{}"'), cnm), new_sn) 
                if not new_sn:  break
            if not new_sn:  continue#while
            pre_cid = sndt.get_cmdid(new_sn)
            if pre_cid:
                pre_cnm = sndt.get_name(pre_cid)
                if app.msg_box(f(_('Snip "{}" is already assigned '
                                   '\nto command "{}".'
                                   '\n'
                                   '\nDo you want to reassign the snip '
                                   '\nto command "{}"?')
                                , new_sn, pre_cnm, cnm), app.MB_OKCANCEL)==app.ID_CANCEL: continue#while
            sndt.set(new_sn, cmd_id)

        elif btn=='help':
            DW, DH      = DLG_W-2*GAP, DLG_H-2*GAP
            dlg_wrapper(_('Help for "Config Hotkeys"'), DLG_W, DLG_H,
                 [dict(cid='htxt',tp='me'    ,t=GAP  ,h=DH-28,l=GAP          ,w=DW   ,props='1,0,1'  ) #  ro,mono,border
                 ,dict(cid='-'   ,tp='bt'    ,t=GAP+DH-23    ,l=GAP+DW-80    ,w=80   ,cap=_('&Close'))
                 ], dict(htxt=
                            _('• In Command.')
                       +c13+ccnd_h
                       +c13+' '
                       +c13+_('• In Hotkeys. ')
                       +c13+kcnd_h
                       +c13+' '
                       +('' if not sndt else ''
                       +c13+_('• In Snip. ')
                       +c13+scnd_h
                       +c13+' '
                       )
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
    keys        = apx._json_loads(open(keys_json).read()) if os.path.isfile(keys_json) else {}

    cmdinfos    = []
    pass;                      #LOG and log('app.app_api_version()={}',(app.app_api_version()))
    if True: # app.app_api_version()>='1.0.212':
        lcmds   = app.app_proc(app.PROC_GET_COMMANDS, '')
        cmdinfos= [('Commands'
                   ,cmd['name']
                   ,cmd['key1']
                   ,cmd['key2']
                   ,cmd['cmd']
                   )
                        if cmd['type']=='cmd' else 
                   ('Plugins'
                   ,cmd['name']
                   ,cmd['key1']
                   ,cmd['key2']
                   ,f('{},{},{}', cmd['p_module'], cmd['p_method'], cmd['p_method_params']).rstrip(',')
                   )
                        for cmd in lcmds
                        if cmd['type']!='lexer'
                ]
        pass;                  #LOG and log('call PROC_GET_COMMANDS',())
#   if app.app_api_version()<'1.0.212':
#       # Core cmds
#       pass;                  #LOG and open(r'py\cuda_config_keys\t.log', 'w')
#       for n in itertools.count():
#           # 5      ,'smth', 'Shift+Ctrl+F1', 'Alt+Q * Ctrl+T'
#           cmdinfo = app.app_proc(app.PROC_GET_COMMAND, str(n))
#           if cmdinfo is None:             break       #for n
#           if cmdinfo[0]<=0:               continue    #for n
#           # Add default category
#           cmdinfo = ('Commands', cmdinfo[1], cmdinfo[2], cmdinfo[3], cmdinfo[0])
#
#           ctg, name, keys1, keys2, cid = cmdinfo
#           if name.endswith(r'\-'):        continue#for n      # command for separator in menu
#           if name.startswith('lexer:'):   continue#for n      # ?? lexer? smth-more?
#           if name.startswith('plugin:'):  continue#for n      # ?? plugin? smth-more?
#
#           pass;              #LOG and open(r'py\cuda_config_keys\t.log', 'a').write(pf(('cmd', n, cmdinfo))+'\n')
#           cmdinfos += [cmdinfo]
#          #for n
#   
#       # Plugin cmds
#       for n in itertools.count():
#           if not    app.app_proc(app.PROC_GET_COMMAND_PLUGIN, str(n)): break#for n
#           (cap
#           ,modul
#           ,meth
#           ,par
#           ,lxrs)  = app.app_proc(app.PROC_GET_COMMAND_PLUGIN, str(n))
#           if cap.endswith(r'\-'):         continue#for n      # command for separator in menu
#           pass;             #LOG and open(r'py\cuda_config_keys\t.log', 'a').write(pf(('plg', n, (cap,modul,meth,par,lxrs)))+'\n')
#           plug_id = modul+','+meth+(','+par if par else '')
#           dct_keys= keys.get(plug_id, {})
#       
#           cmdinfos += [('Plugins'
#                       , 'plugin: '+cap.replace('&', '').replace('\\', ': ')
#                       , ' * '.join(dct_keys.get('s1', []))
#                       , ' * '.join(dct_keys.get('s2', []))
#                       , f('{},{},{}', modul, meth, par).rstrip(',')
#                       )]
#          #for n
#       pass;                  #LOG and log('call PROC_GET_COMMAND_PLUGIN',())
    pass;                      #LOG and log('app.app_api_version()={}',(app.app_api_version()))
    return cmdinfos
   #def collect_keys

#######################################################
if __name__ == '__main__':
    pass;                       print('OK')

""" TODO
[+][kv-kv][11dec15] Init
[+][kv-kv][10may16] Shift HK-2 to HK-1 after del HK-1
[ ][kv-kv][10may16] @ in "In cmd" for filter in keys
[ ][kv-kv][27may16] Remove & to filter
[ ][kv-kv][27may16] Force unhide cmd after RemoveK 
"""
