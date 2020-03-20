import json
import traceback
from django.http import HttpResponseBadRequest, JsonResponse
from server.models import Document
import datetime
from django.views.decorators.csrf import csrf_exempt, csrf_protect


@csrf_exempt
def get_news(request):
    """ 获取所有新闻"""
    try:
        args = request.body
        args = json.loads(args.decode('utf-8'))
        limit = int(args.get('limit', 20))
        offset = int(args.get('offset', 0))
    except Exception as e:
        traceback.print_exc()
        limit = 20
        offset = 0
    try:
        end = offset+limit
        res = Document.objects.order_by('-createtime')[offset:end].values()
        total = Document.objects.count()
    except Exception as e:
        res = []
        total = 0
    return JsonResponse({
        "status": "SUCCESS",
        "total": total,
        "data": list(res)
    })


def try_parse_time(time_str):
    format_list = ['%Y%m%d', '%Y-%m-%d']
    parsed_time = ''
    for format_str in format_list:
        try:
            parsed_time = datetime.datetime.strptime(time_str, format_str)
        except:
            pass
        if parsed_time != '':
            break
    return parsed_time


def set_null_time(request):
    res = Document.objects.filter(createtime__isnull=True).values()
    for item in res:
        parsed_time = ''
        if item['url']:
            tokens = item['url'].split('/')
            for token in tokens:
                if token == '':
                   continue
                if token[0] == 't':
                   tmp_list = token[1:].split('_')
                   token = tmp_list[0]
                parsed_time = try_parse_time(token)
                if parsed_time != '':
                    break
        if parsed_time != '':
            Document.objects.filter(id=item['id']).update(createtime=parsed_time, updatetime=parsed_time)

    return JsonResponse({
        "status": "SUCCESS"
    })
