''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github)
Version:
    '2.1.7 2021-03-03'
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

pass;                           LOG     = (-9== 9)  # Do or dont logging.
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
    pass;                      #LOG and log('ex={}',(ex))
    pass
#sndt        = None

VERSION     = re.split('Version:', __doc__)[1].split("'")[1]
VERSION_V,  \
VERSION_D   = VERSION.split(' ')


class Command:
    def dlg_config_keys(self):
#       if app.app_api_version()<'1.0.136':     # dlg_hotkey, PROC_GET_HOTKEY, PROC_SET_HOTKEY
        if app.app_api_version()<'1.0.212':     # depr PROC_GET_COMMAND, PROC_GET_COMMAND_PLUGIN
            return app.msg_status(_('Need update CudaText'))
        CfgKeysDlg().show()
       #def dlg_config_keys
   #class Command

def collect_keys():
    keys_json   = os.path.join(app.app_path(app.APP_DIR_SETTINGS), 'keys.json')
    keys        = apx._json_loads(open(keys_json).read()) if os.path.isfile(keys_json) else {}

    cmdinfos    = []
    pass;                      #LOG and log('app.app_api_version()={}',(app.app_api_version()))
#   if True: # app.app_api_version()>='1.0.212':
    lcmds       = app.app_proc(app.PROC_GET_COMMANDS, '')
    cmdinfos    = [('Plugins'
                   ,cmd['name']
                   ,cmd['key1']
                   ,cmd['key2']
                   ,f('{},{},{}', cmd['p_module'], cmd['p_method'], cmd['p_method_params']).rstrip(',')
                   )
                        if cmd['type']=='plugin' else 
                   ('Commands'
                   ,cmd['name']
                   ,cmd['key1']
                   ,cmd['key2']
                   ,cmd['cmd']
                   )
                        for cmd in lcmds
                        if cmd['type'] in ('plugin', 'cmd')
#                       if cmd['type']!='lexer'
                ]
    return cmdinfos
   #def collect_keys

class CfgKeysDlg():
    @staticmethod
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

    COL_WS      = [310, 160, 160, 135]
    COL_WS      = [COL_WS[0]+COL_WS[3]]+COL_WS[1:3]+[0] if not sndt else COL_WS
    LST_W, LST_H= sum(COL_WS)+20, 200-5
    DLG_W, DLG_H= 5+LST_W+5+100+5, 5+LST_H+105+5+3
    lfk1        = 5+COL_WS[0]+5
    lfk2        = 5+COL_WS[0]+COL_WS[1]+5
    lfsn        = 5+COL_WS[0]+COL_WS[1]+COL_WS[2]+5
    lrpt        = DLG_W-5-100
    ccnd_h      = _('Suitable command names will contain all specified words.'
                    '\nTips:'
                  '\n · Use "_" for word boundary.'
                  '\n   "_up" selects "upper" but not "group".')
    kcnd_h      = _('Suitable command hotkeys will contain all specified words.'
                  '\nTips:'
                  '\n · Use "_" for key-name boundary.'
                  '\n   "_f" selects "F1" and "Ctrl+F" but not "Left".')
    scnd_h      = _('Suitable command snips will match specified string.'
                  '\nUsage:'
                  '\n · Type "/" and snip string and push Tab-key.'
                  '\nTips:'
                  '\n · Use ? for any character and * for any fragment.')
    addk_h      = _('Set hotkey for command (if no one).'
                  '\nExtend to series hotkeys (if command already has hotkeys).')
    hrpt_h      = _('Shows HTML page with report of all hotkeys in editor.'
                  '\nThe report is usefull to analyze hotkeys in a whole.')
    trpt_h      = _('Show compact report of hotkeys in new tab.'
                  '\nThe report is usefull to find free hotkeys.')
    cpnm_h      = _('Copy command name to clipboard')
    open_h      = _('Open source of plugin code')
    sort_h      = _('Sort data by click on table header' # or by hotkeys Alt+1, Alt+2, Alt+3'
                  '\n3-stage loop of sorting:'
                  '\n · in alphabetical order,'
                  '\n · in reverse alphabetical order,'
                  '\n · in natural order (as at start)'
                    )
    reND    = re.compile(r'\W')

    def __init__(self):
        m,M         = self,self.__class__

        m.sort      = ('', True)
        m.cmd_id    = ''
        m.ccnd      = ''
        pass;                  #m.ccnd      = 'space'
        m.kcnd      = ''
        m.scnd      = ''
        m.orcn      = False
        m.orsn      = False
        m.fid       = 'ccnd'

        m.nkki_l,   \
        m.id2nkks,  \
        m.ks2id     = M.prep_keys_info()
        pass;                  #LOG and log('nkki_l={}',(pf(m.nkki_l)))
       #def __init__
    
    def show(self):
        m,M         = self,self.__class__
        m.ag    = DlgAgent(
            form =dict(cap     = f(_('Configure Hotkeys ({})'), VERSION_V)
                      ,resize  = True                              ##!!
                      ,w       = M.DLG_W,   w_max   = M.DLG_W
                      ,h       = M.DLG_H                            #,   h_max   = M.DLG_H
                      )
        ,   ctrls=self.get_cnts()
        ,   vals =self.get_vals()
        ,   fid  =m.fid
                            ,   options = {
                               #'gen_repro_to_file':'repro_dlg_cfg_keys.py',
                                }
        )
        m.ag.show()
       #def show
    
    def get_cnts(self, what=''):
        m,M         = self,self.__class__
        open_src    = apx.get_opt('config_keys_with_open', False)
        sndt_b      = bool(sndt)
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
                text    = '·' + M.reND.sub('·', text)    + '·'
                cnd_s   = ' ' + cnd_s + ' '
                cnd_s   = cnd_s.replace(' _', ' ·').replace('_ ', '· ')
            pass;                  #LOG and log('cnd_s, text={}',(cnd_s, text))
            return all(map(lambda c:c in text, cnd_s.split()))
        def bmix(val1, bor12, val2, bor23, val3):
            val12   = val1  or val2     if bor12 else        val1  and val2
            return    val12 or val3     if bor23 else        val12 and val3
#       def bmix(bor12, bor23, val1, val2, val3):
#           val12   = val1  or val2     if bor12 else        val1  and val2
#           return    val12 or val3     if bor23 else        val12 and val3

        ccnd_u  = m.ccnd.upper()
        kcnd_u  = m.kcnd.upper()
        pass;                  #LOG and log('ccnd_u, kcnd_u, scnd={}',(ccnd_u, kcnd_u, m.scnd))
        nkkis_l = [    (nm, k1, k2, id, sndt.get_snips(id) if sndt else [])
                   for (nm, k1, k2, id)   in m.nkki_l]
        pass;                  #LOG and log('nkkis_l={}',(pf(nkkis_l)))
        fl_NKKISs=[    (nm, k1, k2, id, sns)
                   for (nm, k1, k2, id, sns)   in nkkis_l
                   if  bmix( (not ccnd_u or               test_cond(ccnd_u, nm))
                                ,m.orcn and (ccnd_u and kcnd_u)
                            ,(not kcnd_u or               test_cond(kcnd_u, k1, k2, 'keys'))
                                ,m.orsn and (m.scnd)
                            ,(not m.scnd or not sndt   or is_cond4snps(m.scnd, sns)) 
                            )
                  ]
#                  if  bmix(m.orcn, m.orsn
#                                 ,(not ccnd_u or               test_cond(ccnd_u, nm))
#                                 ,(not kcnd_u or               test_cond(kcnd_u, k1, k2, 'keys'))
#                                 ,(not m.scnd or not sndt   or is_cond4snps(m.scnd, sns)) )]
        sort_n  = apx.icase(m.sort[0]=='nm',0, m.sort[0]=='k1',1, m.sort[0]=='k2',2, m.sort[0]=='sn',4, 0)   # index in item of fl_NKKISs
        sort_c  = '' if not m.sort[0] else ' ▲' if m.sort[1] else ' ▼'
        if m.sort[0]: 
            fl_NKKISs   = sorted(fl_NKKISs, key=lambda mkkis:('_' if not mkkis[sort_n] and not m.sort[1] else mkkis[sort_n]), reverse=m.sort[1])
#           fl_NKKISs   = sorted(fl_NKKISs, key=lambda mkkis:mkkis[sort_n], reverse=m.sort[1])
        stat_c  = f(' ({}/{})',len(fl_NKKISs), len(nkkis_l))                                + (sort_c if m.sort[0]=='nm' else '')
        stat_k1 = f(' ({}/{})',sum(1 if k1  else 0 for (nm, k1, k2, id, sns) in fl_NKKISs)  
                              ,sum(1 if k1  else 0 for (nm, k1, k2, id, sns) in nkkis_l))   + (sort_c if m.sort[0]=='k1' else '')
        stat_k2 = f(' ({}/{})',sum(1 if k2  else 0 for (nm, k1, k2, id, sns) in fl_NKKISs)
                              ,sum(1 if k2  else 0 for (nm, k1, k2, id, sns) in nkkis_l))   + (sort_c if m.sort[0]=='k2' else '')
        stat_s  = f(' ({}/{})',sum(1 if sns else 0 for (nm, k1, k2, id, sns) in fl_NKKISs)
                              ,sum(1 if sns else 0 for (nm, k1, k2, id, sns) in nkkis_l))   + (sort_c if m.sort[0]=='sn' else '')
        m.fl_Is = [id         for (nm, k1, k2, id, sn) in fl_NKKISs ]   ##!!
        itms    = (list(zip([_('Command')+stat_c, _('Hotkey-1')+stat_k1, _('Hotkey-2')+stat_k2, _('Snips')+stat_s], map(str, M.COL_WS)))
                  ,         [ (nm,                 k1,             k2,          ', '.join(sns)) 
                                for  (nm, k1, k2, id, sns) in fl_NKKISs ]
                  )
        if what=='lwks':
            return [('lwks',dict(items=itms))]

        cnts    =[
  ('fltr',dict(tp='bt'  ,t=5+40+10      ,l=M.lrpt   ,w=100  ,cap=_('&Filter')           ,ex0='1'                    ,call=m.do_fltr )) # &f  default
 ,('drop',dict(tp='bt'  ,t=5+70+10      ,l=M.lrpt   ,w=100  ,cap=_('&All')                                          ,call=m.do_fltr )) # &a
 ,('orcn',dict(tp='ch'  ,t=5            ,l=M.lfk1-60,w=40   ,cap=_('&OR')                                           ,call=m.do_fltr )) # &o
 ,('orsn',dict(tp='ch'  ,t=5            ,l=M.lfsn-60,w=40   ,cap=_('O&R')                               ,vis=sndt_b ,call=m.do_fltr )) # &r
 ,('ccn_',dict(tp='lb'  ,tid='orcn'     ,l=5+5      ,w=90   ,cap=_('In &Command:')      ,hint=M.ccnd_h                              )) # &c
 ,('ccnd',dict(tp='ed'  ,t=5+20         ,l=5+5      ,w=150                                                                          )) #
 ,('kcn_',dict(tp='lb'  ,tid='orcn'     ,l=M.lfk1   ,w=50   ,cap=_('In &Hotkeys:')      ,hint=M.kcnd_h                              )) # &h
 ,('kcnd',dict(tp='ed'  ,t=5+20         ,l=M.lfk1   ,w=120                                                                          )) #
                                                                                                                            
 ,('scn_',dict(tp='lb'  ,tid='orsn'     ,l=M.lfsn   ,w=50   ,cap=_('In &Snip(s):')        ,hint=M.scnd_h  ,vis=sndt_b                 )) # &s
 ,('shlp',dict(tp='bt'  ,tid='orsn'     ,l=M.lfsn+80,w=20   ,cap=_('&?')                                ,vis=sndt_b ,call=m.do_shlp )) # &?
 ,('scnd',dict(tp='ed'  ,t=5+20         ,l=M.lfsn   ,w=100                                              ,vis=sndt_b                 )) #
                                                                                                                                    
#,('srt0',dict(tp='bt'  ,t  =0          ,l=1000     ,w=0    ,cap=_('&1')    ,sto=F                                  ,call=m.do_sort ))# &1
#,('srt1',dict(tp='bt'  ,t  =0          ,l=1000     ,w=0    ,cap=_('&2')    ,sto=F                                  ,call=m.do_sort ))# &2
#,('srt2',dict(tp='bt'  ,t  =0          ,l=1000     ,w=0    ,cap=_('&3')    ,sto=F                                  ,call=m.do_sort ))# &3
#,('srt3',dict(tp='bt'  ,t  =0          ,l=1000     ,w=0    ,cap=_('&4')    ,sto=F                      ,vis=sndt_b ,call=m.do_sort ))# &4
 ,('lwks',dict(tp='lvw' ,t=5+50         ,l=5        ,w=M.LST_W,h=M.LST_H    ,items=itms ,ex0='1'        ,a='tB'                     
                                                                ,on_click_header=lambda idd, idc, data:m.wn_sort(data)              )) #     grid
                                                                                                                                    
 ,('cpnm',dict(tp='bt'  ,t=M.DLG_H-60   ,l=5+5      ,w=110  ,cap=_('Copy &name')        ,hint=M.cpnm_h  ,a='TB'     ,call=m.do_code )) # &n
 ,('open',dict(tp='bt'  ,t=M.DLG_H-30   ,l=5+5      ,w=110  ,cap=_('Open code &#')      ,hint=M.open_h  ,a='TB'     ,call=m.do_code )) # &#
 ,('hrpt',dict(tp='bt'  ,t=M.DLG_H-60   ,l=130      ,w=150  ,cap=_('Report to HT&ML')   ,hint=M.hrpt_h  ,a='TB'     ,call=m.do_rprt )) # &m
 ,('trpt',dict(tp='bt'  ,t=M.DLG_H-30   ,l=130      ,w=150  ,cap=_('Report to new &Tab'),hint=M.trpt_h  ,a='TB'     ,call=m.do_rprt )) # &t
 ,('add1',dict(tp='bt'  ,t=M.DLG_H-60   ,l=M.lfk1   ,w=150  ,cap=_('Set/Add Hotkey-&1') ,hint=M.addk_h  ,a='TB'     ,call=m.do_work )) # &1
 ,('del1',dict(tp='bt'  ,t=M.DLG_H-30   ,l=M.lfk1   ,w=150  ,cap=_('Remove Hotkey-1 &!')                ,a='TB'     ,call=m.do_work )) # &!
 ,('add2',dict(tp='bt'  ,t=M.DLG_H-60   ,l=M.lfk2   ,w=150  ,cap=_('Set/Add Hotkey-&2') ,hint=M.addk_h  ,a='TB'     ,call=m.do_work )) # &2
 ,('del2',dict(tp='bt'  ,t=M.DLG_H-30   ,l=M.lfk2   ,w=150  ,cap=_('Remove Hotkey-2 &@')                ,a='TB'     ,call=m.do_work )) # &@
 ,('asnp',dict(tp='bt'  ,t=M.DLG_H-60   ,l=M.lfsn   ,w=150  ,cap=_('Set/A&dd Snip')     ,vis=sndt_b     ,a='TB'     ,call=m.do_work )) # &d
 ,('rsnp',dict(tp='bt'  ,t=M.DLG_H-30   ,l=M.lfsn   ,w=150  ,cap=_('R&emove Snip(s)')   ,vis=sndt_b     ,a='TB'     ,call=m.do_work )) # &e
 ,('help',dict(tp='bt'  ,t=M.DLG_H-60   ,l=M.lrpt   ,w=100  ,cap=_('Hel&p')                             ,a='TB'     ,call=m.do_shlp )) # &p 
                ]
        return cnts
       #def get_cnts
    
    def get_vals(self, what=''):
        m,M         = self,self.__class__
        lwks_n  = -1                                 \
                    if 0==len(m.fl_Is)          else \
                   0                                 \
                    if m.cmd_id not in m.fl_Is  else \
                   m.fl_Is.index(m.cmd_id)
        if what=='lwks':
            return      dict(lwks=lwks_n)
        
        vals    =       dict(ccnd=m.ccnd
                            ,kcnd=m.kcnd
                            ,orcn=m.orcn
                            ,lwks=lwks_n)
        if sndt:
            vals.update(dict(scnd=m.scnd
                            ,orsn=m.orsn
            ))
        return vals
       #def get_vals
    
    def do_rprt(self, aid, ag, data=''):
        m,M         = self,self.__class__
        if False:pass
        elif aid=='trpt':
            # Compact report to tab
            app.file_open('')
            ed.set_text_all(get_str_report())

        elif aid=='hrpt':
            # Full report to HTML
            htm_file = os.path.join(tempfile.gettempdir(), '{}_keymapping.html'.format(app_name))
            do_report(htm_file)
            webbrowser.open_new_tab('file://'+htm_file)
            app.msg_status(_('Opened browser with file ')+htm_file)
        return []
       #def do_rprt
    
    def do_shlp(self, aid, ag, data=''):
        m,M         = self,self.__class__
        DW, DH      = 500-2*GAP, 500-2*GAP
        dlg_wrapper(_('Help for "Config Hotkeys"'), 500, 500,
             [dict(cid='htxt',tp='me'    ,t=GAP  ,h=DH-28,l=GAP          ,w=DW   ,ex0='1', ex1='0', ex2='1'  ) #  ro,mono,border
             ,dict(cid='-'   ,tp='bt'    ,t=GAP+DH-23    ,l=GAP+DW-80    ,w=80   ,cap=_('&Close'))
             ], dict(htxt=
                     f(_('• In Command.\n{}'
                       '\n\n• In Hotkeys.\n{}'
                       '{}'
                       '\n\n• Set/Add.\n{}'
                       '\n\n• HTML-report.\n{}'
                       '\n\n• Tab-report.\n{}'
                       '\n\n• Sorting.\n{}'),
                       M.ccnd_h, M.kcnd_h,
                       f(_('\n\n• In Snip.\n{}'), M.scnd_h) if sndt else '',
                       M.addk_h, M.hrpt_h, M.trpt_h, M.sort_h)
                    ), focus_cid='htxt')
        return []
       #def do_shlp
    
    def do_code(self, aid, ag, data=''):
        m,M         = self,self.__class__
        
        lwks_n  = ag.cval('lwks')
        if lwks_n==-1:                      return [] #continue#while
        m.cmd_id  = m.fl_Is[lwks_n]
        pass;                  #LOG and log('m.fl_Is={}',(m.fl_Is))
        pass;                  #LOG and log('lwks_n,m.cmd_id={}',(lwks_n,m.cmd_id))
        if False:pass
        elif aid=='cpnm':
            cmd_nkk = m.id2nkks[m.cmd_id]
            app.app_proc(app.PROC_SET_CLIP, cmd_nkk[0])
        
        elif aid=='open':
            pass;               LOG and log('m.cmd_id={}',(m.cmd_id))
            if type(m.cmd_id)!=str:         return [] #continue#while
            plug_mdl,   \
            plug_mth    = m.cmd_id.split(',')[0:2]
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
            if plug_mth not in plug_body:   return [] #continue#while
            # Open
            app.file_open(plug_py)
            # Locate
            user_opt= app.app_proc(app.PROC_GET_FINDER_PROP, '') \
                        if app.app_api_version()>='1.0.248' else \
                      app.app_proc(app.PROC_GET_FIND_OPTIONS, '')   # Deprecated
            ed.cmd(cmds.cmd_FinderAction, chr(1).join([]
                +['findnext']
                +[plug_mth]
                +['']
                +['fa']
            ))
            if app.app_api_version()>='1.0.248':
                app.app_proc(app.PROC_SET_FINDER_PROP, user_opt)
            else:
                app.app_proc(app.PROC_SET_FIND_OPTIONS, user_opt)   # Deprecated
            return None #break#while
        return []
       #def do_code
    
    def wn_sort(self, col):
        pass;                  #LOG and log('col={}',(col))
        m,M         = self,self.__class__

        col_s       = 'nm' if col==0 else \
                      'k1' if col==1 else \
                      'k2' if col==2 else \
                      'sn'
        srt_s       = m.sort[0]
        m.sort      = (col_s, False)                            \
                        if not srt_s                      else  \
                      (col_s, False)                            \
                        if srt_s!=col_s                   else  \
                      (srt_s, True)                             \
                        if srt_s==col_s and not m.sort[1] else  \
                      ('', True)
        pass;                  #LOG and log('m.sort={}',(m.sort))
        lwks_n      = m.ag.cval('lwks')
        pass;                  #LOG and log('lwks_n={}',(lwks_n))
        m.cmd_id    = '' if lwks_n==-1 else m.fl_Is[lwks_n]
        lwks_its_v  = odict(             self.get_cnts('lwks'))
        lwks_its_v['lwks'].update({'val':self.get_vals('lwks')['lwks']})    if lwks_n>0 else 0  # Save "non-trivial" selection
#       lwks_its_v['lwks'].update(self.get_vals('lwks'))                    ##!! :(
        m.ag.update(
                    ctrls=lwks_its_v
                )
        return []
       #def wn_sort
    
    def do_sort(self, aid, ag, data=''):
        return self.wn_sort(int(aid[3]))    # srtN
       #def do_sort
    
    def do_fltr(self, aid, ag, data=''):
        m,M         = self,self.__class__

        lwks_n      = ag.cval('lwks')
        m.cmd_id    = '' if lwks_n==-1 else m.fl_Is[lwks_n]
        if False:pass
        elif aid in ('fltr', 'orcn', 'orsn'):
            m.ccnd  = ag.cval('ccnd').strip()
            m.kcnd  = ag.cval('kcnd').strip()
            m.scnd  = ag.cval('scnd').strip()   if sndt else ''
            m.orcn  = ag.cval('orcn')
            m.orsn  = ag.cval('orsn')           if sndt else False
            fid     = 'lwks'
        elif aid=='drop':
            m.ccnd  = ''
            m.kcnd  = ''
            m.scnd  = ''
            fid     = 'ccnd'
        return dict(ctrls=self.get_cnts('lwks')
                ,   vals =self.get_vals('lwks')
                ,   fid  =fid
                )
       #def do_fltr
    
    def do_work(self, aid, ag, data=''):
        m,M         = self,self.__class__

        lwks_n      = ag.cval('lwks')
        if lwks_n==-1:                      return [] #continue#while
        m.cmd_id    = m.fl_Is[lwks_n]
        if False:pass
        elif aid in ('del1', 'del2'):
            # Delete the hotkeys
            cmd_nkk = m.id2nkks[m.cmd_id]
            del_i   = 1 if aid=='del1' else 2
            if not cmd_nkk[del_i]:          return [] #continue#while
            cmd_nkk[del_i]  = ''
            if  cmd_nkk[2]:
                cmd_nkk[1]  = cmd_nkk[2]
                cmd_nkk[2]  = ''
            set_ok  = app.app_proc(app.PROC_SET_HOTKEY, f('{}|{}|{}', m.cmd_id, cmd_nkk[1], cmd_nkk[2]))
            if not set_ok:  log('Fail to use PROC_SET_HOTKEY for cmd "{}"', m.cmd_id)
            m.nkki_l,   \
            m.id2nkks,  \
            m.ks2id     = M.prep_keys_info()
        
        elif aid in ('add1', 'add2'):
            ext_k   = app.dlg_hotkey()
            pass;              #LOG and log('ext_k={}',(ext_k,))
            if ext_k is None:               return [] #continue#while
            cmd_nkk = m.id2nkks[m.cmd_id]
            add_i   = 1 if aid=='add1' else 2
            old_k   = cmd_nkk[add_i]
            new_k   = old_k + ' * ' + ext_k if old_k else ext_k
            pass;              #LOG and log('cmd_nkk,old_k,new_k={}',(cmd_nkk,old_k,new_k))
            if new_k in m.ks2id:
                dbl_id  = m.ks2id[new_k]
                dbl_nkk = m.id2nkks[dbl_id]
                if app.msg_box(f(_('Hotkey "{}" is already assigned '
                                   '\nto command "{}".'
                                   '\n'
                                   '\nDo you want to reassign the hotkey '
                                   '\nto selected command "{}"?')
                                , new_k, dbl_nkk[0], cmd_nkk[0]), app.MB_OKCANCEL)==app.ID_CANCEL: return [] #continue#while
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
            set_ok  = app.app_proc(app.PROC_SET_HOTKEY, f('{}|{}|{}', m.cmd_id, cmd_nkk[1], cmd_nkk[2]))
            if not set_ok:  log('Fail to use PROC_SET_HOTKEY for cmd "{}"', m.cmd_id)
            m.nkki_l,   \
            m.id2nkks,  \
            m.ks2id     = M.prep_keys_info()
        
        elif aid=='asnp' and sndt:
            cnm     = sndt.get_name(m.cmd_id)
            new_sn  = app.dlg_input(f(_('Add snip for "{}"'), cnm), '') 
            if not new_sn:                  return [] #continue#while
            while not SnipData.is_snip(new_sn):
                app.msg_status(SnipData.msg_correct_snip)
                new_sn  = app.dlg_input(f(_('Snip for "{}"'), cnm), new_sn) 
                if not new_sn:  break
            if not new_sn:                  return [] #continue#while
            pre_cid = sndt.get_cmdid(new_sn)
            if pre_cid:
                pre_cnm = sndt.get_name(pre_cid)
                if app.msg_box(f(_('Snippet "{}" is already assigned'
                                   '\nto command "{}".'
                                   '\n'
                                   '\nDo you want to reassign the snippet'
                                   '\nto command "{}"?')
                                , new_sn, pre_cnm, cnm), app.MB_OKCANCEL)==app.ID_CANCEL: return [] #continue#while
            sndt.set(new_sn, cmd_id)

        elif aid=='rsnp' and sndt: 
            cnm     = sndt.get_name(m.cmd_id)
            snp_l   = sndt.get_snips(m.cmd_id)
            snps    = ', '.join(snp_l)
            if app.msg_box(f(_('Do you want to remove snip(s) '
                               '\n    {}'
                               '\nfor command "{}"?')
                            , snps, cnm), app.MB_OKCANCEL)==app.ID_CANCEL: return [] #continue#while
            for snp in snp_l:
                sndt.free(snp)

        return dict(ctrls=self.get_cnts('lwks')
                ,   vals =self.get_vals('lwks')
                ,   fid  ='lwks'
                )
       #def do_work
    
   #class CfgKeysDlg

#######################################################
if __name__ == '__main__':
    pass;                       print('OK')

""" TODO
[+][kv-kv][11dec15] Init
[+][kv-kv][10may16] Shift HK-2 to HK-1 after del HK-1
[ ][kv-kv][10may16] @ in "In cmd" for filter in keys
[ ][kv-kv][27may16] Remove & to filter
[ ][kv-kv][27may16] Force unhide cmd after RemoveK 
[ ][kv-kv][01mar18] Bug: <'smth' OR ''> show all
"""
