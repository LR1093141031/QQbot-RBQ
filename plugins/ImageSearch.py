from nonebot import on_command, CommandSession
import sys
import os
import time
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
from .module import SauceNao, Ascii2d, Tx, Group_Permission

download_path = os.path.split(os.path.realpath(__file__))[0] + '/data/temp'
if not os.path.exists(download_path):
    os.makedirs(download_path)


@on_command('SauceNaotu', aliases=('搜图', '识图', '找图'), only_to_me=False)
async def SauceNaotu(session: CommandSession):
    permission = Group_Permission.Permission()  # 检查权限
    if session.ctx['message_type'] == 'group':  # 这里不确定是否只检查群权限
        enable = permission.permission_check(session.ctx['group_id'], 'SauceNaotu')
        print('=========', enable)
        if enable is False:
            await session.send('无权限执行该命令')
            return
        else:
            pass

    pic_url = session.get('pic_id', prompt='混合搜图 请发送图片或url链接')
    tx_report = Tx.img_downloader(download_path, pic_url)
    if tx_report is False:
        await session.send('无法识别到图片或url,请重试')
        return False

    time_start = time.time()

    saucenao = SauceNao.SauceNao()
    ascii2d = Ascii2d.Ascii2d()
    saucenao_dict = saucenao.search(tx_report)  # (img_url, correct_rate, result_title, result_content)
    ascii2d_dict = ascii2d.search(tx_report)
    if (saucenao_dict is False) and (ascii2d_dict is False):
        await session.send(f'{saucenao.state}  {ascii2d.state}')
        return False
    search_text = ''
    if saucenao_dict:
        saucenao_result_num = len(saucenao_dict['img_url'])
        saucenao_file_list = saucenao.pic_download(download_path)  # 下载全部结果图片，返回为列表
        search_text += f'''SauceNao搜图结果\n{saucenao_result_num}个搜索结果\n'''
        for i in range(saucenao_result_num):
            search_text += f'''标题:{saucenao_dict['result_title'][i]}\n相似度:{saucenao_dict['correct_rate']
            [i]}\n{saucenao_dict['result_content'][i]}\n[CQ:image,file=file:///{saucenao_file_list[i]}]\n'''
    if ascii2d_dict:
        ascii2d_result_num = len(ascii2d_dict['img_url'])
        ascii2d_file_list = ascii2d.pic_download(download_path)
        search_text += f'''Ascii2d搜图结果\n{ascii2d_result_num}个搜索结果\n'''
        for i in range(ascii2d_result_num):
            search_text += f'''标题:{ascii2d_dict['result_title'][i]}\n相似度:{ascii2d_dict['correct_rate']
            [i]}\n{ascii2d_dict['result_content'][i]}\n[CQ:image,file=file:///{ascii2d_file_list[i]}]\n'''
    time_stop = time.time()
    time_use = time_stop - time_start
    search_text += f'本次搜索用时{int(time_use)}秒'
    await session.send(search_text)


@SauceNaotu.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            print('================stripped', stripped_arg)
            session.state['pic_url'] = stripped_arg
        return
    else:
        if (session.ctx['raw_message'] is None) or (session.ctx['raw_message'] == ''):
            print('--------------------raw', session.ctx['raw_message'])
            session.pause('发送图片或url链接')
