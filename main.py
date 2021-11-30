"""
robot消息路由基本框架
@group: nonesrc
@author: deelter
@time: 2021-11-30
@version: 1.0
"""

# 单独关键词 -> 方法 映射
single_func_maps = dict()

# 包含关键词 -> 方法 映射
sub_find_func_maps = dict()


def add_func_route(key_name_args, func, all_case_matching=False, sub_find=False):
    def add_matched_func(_key_name_args, _func, _sub_find):
        if _key_name_args in (single_func_maps, sub_find_func_maps):
            return
        if _sub_find:
            sub_find_func_maps[_key_name_args] = _func
        else:
            single_func_maps[_key_name_args] = _func

    if isinstance(key_name_args, str):
        add_matched_func(key_name_args, func, sub_find)
        if not all_case_matching:
            add_matched_func(key_name_args.lower(), func, sub_find)
    elif isinstance(key_name_args, list):
        for item in key_name_args:
            if not isinstance(item, str):
                raise RuntimeError('不支持的列表内映射参数类型！')
            else:
                add_matched_func(item, func, sub_find)
                if not all_case_matching:
                    add_matched_func(item.lower(), func, sub_find)
    else:
        raise RuntimeError('不支持的映射参数类型！')


def robot_msg_route(key_name_args, all_case_matching=False, sub_find=False):
    """
    robot消息路由mapping装饰器
    :param key_name_args: 消息关键词
    :param all_case_matching: 是否完全一致匹配
    :param sub_find: 是否允许进行关键词子字符串查询
    :return: 经过装饰后的方法
    """

    def set_name(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        add_func_route(key_name_args, func, all_case_matching, sub_find)

        return wrapper

    return set_name


def router_handler(key_name):
    def matched_from_single(k):
        target_func = single_func_maps.get(key_name)
        if target_func is None:
            target_func = single_func_maps.get(key_name.lower())
        return target_func

    def matched_from_sub_find(k):
        k_lower = k.lower()
        target_func = None
        for item in sub_find_func_maps:
            if item in k or item in k_lower:
                target_func = sub_find_func_maps.get(item)
                break
        return target_func

    matched_func_list = list()
    matched_func_list.append(matched_from_single)
    matched_func_list.append(matched_from_sub_find)
    for func in matched_func_list:
        matched_func = func(key_name)
        if matched_func is not None:
            try:
                if func is matched_from_sub_find:
                    args_tuple = get_msg_args(key_name)
                    func_args_count = matched_func.__code__.co_argcount
                    given_args_count = len(args_tuple)
                    if func_args_count > given_args_count:
                        tmp_list = list(args_tuple)
                        tmp_list[given_args_count:] = [''] * (func_args_count - given_args_count)
                        args_tuple = tuple(tmp_list)
                    matched_func(*args_tuple)
                else:
                    matched_func()
            except TypeError:
                invalid_args_format()
            break
    else:
        not_matched_handler()


def format_args_msg(msg_text):
    msg_text = msg_text.strip(' ')
    text_list = list(msg_text)
    for i in range(len(text_list) - 1, 0, -1):
        if i > 0 and text_list[i] == ' ' and text_list[i - 1] == ' ':
            text_list.pop(i)
    return ''.join(text_list)


def get_msg_args(msg_text):
    args_text = format_args_msg(msg_text).split(' ')[1:]
    return tuple(args_text)


def not_matched_handler():
    print('没有匹配到相应的处理方法！')


def invalid_args_format():
    print('参数格式错误！')


@robot_msg_route(['#help', '#帮助'], sub_find=True)
def show_help():
    print("help")


@robot_msg_route('#login', sub_find=True)
def sign_everyday(username, password):
    print(f'{username} {password} 打卡成功！')


if __name__ == '__main__':
    def say_hello():
        print('hello')


    add_func_route(['#hello', '#你好'], say_hello)

    while True:
        op = input()
        router_handler(op)
