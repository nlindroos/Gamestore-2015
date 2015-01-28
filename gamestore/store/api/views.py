from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.db.models import Q
from json import dumps
from re import match
from django.db.models import Count, Min, Sum, Avg

from store.models import Game


def wildcard_builder(src, attr):
    """
    Given a string, creates a Q object wildcard match.
    
    Attributes:
        src:    The source string possibly containing * wildcards
        attr:   A string: name of the attribute that should be matched
    
    For example:
    
        src = 'test'      ---> attr__iexact : 'test'
        src = '*test'     ---> attr_iendswith : 'test'
        src = 'test*'     ---> attr_istartswith : 'test'
        src = 'te*st'     ---> attr_istartswith : 'te' & attr_iendswith : 'st'
        src = '*test*'    ---> attr_icontains : 'test'
        src = 't*e*st'    ---> attr_istartswith : 't' & attr_icontains : 'e' & attr_iendswith : 'st'
        
    Returns:
        a Q object
    """
    if (src == '*'):
        return Q()
    parts = src.split('*')
    if len(parts) == 1:
        return Q(**{'{}__iexact'.format(attr) : src})
    query = Q()
    if src.startswith('*'):
        query &= Q(**{'{}__icontains'.format(attr) : parts[0]})
    else:
        query &= Q(**{'{}__istartswith'.format(attr) : parts[0]})
    if src.endswith('*'):
        query &= Q(**{'{}__icontains'.format(attr) : parts[-1]})
    else:
        query &= Q(**{'{}__iendswith'.format(attr) : parts[-1]})
    for p in parts[1:-1]:
        query &= Q(**{'{}__icontains'.format(attr) : p})
    return query
    

def api_view(request, titles='', developers='', tags=''):
    """
    RESTfull API view.
    
    Args:
        titles:         string in the form '/title/t1/title/t2/.../title/tn'
        developers:     string in the form '/dev/d1/dev/d2/.../dev/dn'
        tags:           string in the form '/tagged/t1/tagged/t2/.../tagged/tn'
    
    Returns:
        a JSON string, wrapped in a callback function if specified.
    
    The JSON object contains an array of games containing some info:
        - basic game data 
            name, developer, tags, etc.
        - sales [OPTIONAL, using expand=sales]
            total sales, number of purchases 
        - highscores [OPTIONAL, using expand=highscores_n]
            top n highscores including score, player who made the score, time when the score was made
    
    The returned set of games can be limited to (all filters are OPTIONAL):
        - certain game titles
            title/t1/title/t2       --> (title is t1 OR t2)
        - games tagged with certain tags 
            tagged/t1/tagged/t2     --> (tags contain t1 AND t2),   by default or with tagfilter=all
            tagged/t1/tagged/t2     --> (tags contain t1 OR t2),    with tagfilter=any
        - developers with certain names 
            dev/d1/dev/d2           --> (developer is d1 OR d2)
        
    The results can also be expanded using url query string options:
        ?expand=sales
        ?expand=highscores_n (where n is some integer)
    To expand both sales stats and highscores, use a comma separator:
        ?expand=sales,highscores_n
        
    The JSON string can be wrapped in a callback function using the 'callback' query string option:
        &callback=mycoolcallback
        
    The tag filtering can be changed using the 'tagfilter' query string option:
        &tagfilter=any
        &tagfilter=all
    """
    
    title_list = [x for x in titles.split('/title/') if x]
    tag_list = [x for x in tags.split('/tagged/') if x]      
    dev_list = [x for x in developers.split('/dev/') if x]
                    
    subquery1 = Q()
    for t in title_list:
        subquery1 |= wildcard_builder(t, 'title')
    
    subquery2 = Q()
    for d in dev_list:
        subquery2 |= wildcard_builder(d, 'developer__username')
    
    query = (subquery1 & subquery2)
    games = Game.objects.filter(query)
    
    expand = request.GET.get('expand', '').split(',')
    
    # ?expand=sales :
    sales = False
    if 'sales' in expand:
        sales = True
        games = games.annotate(Sum('purchase__fee')).annotate(Count('purchase'))
    # ?expand=highscores_number :
    scores = 0
    for e in expand:
        m = match(r'highscores_((?:\d)+)', e)
        if m:
            try:
                scores = int(m.group(1))
            except ValueError as err:
                pass
            else:
                break
    tagfilter = request.GET.get('tagfilter', 'all')        
    # because tags is a comma separated string, we must handle it separately (outside of the query):
    if tags:
        tag_filtered_games = []
        # yes, 3 nested loops, ugh...
        for g in games:
            matches_found = 0
            for pattern in tag_list:
                p = pattern.replace(r'*', r'.*')
                for t in g.get_tags():
                    if match(p, t):
                        matches_found += 1
                        break
                if tagfilter == 'any' and matches_found > 0:
                    tag_filtered_games.append(g)  
                    break
            if tagfilter != 'any' and matches_found == len(tag_list):
                tag_filtered_games.append(g)  
        games = tag_filtered_games
    
    result = {'games' : []}
          
    for g in games:
        d = {}
        d['title'] = g.title
        d['description'] = g.description
        d['developer'] = g.developer.username
        d['url'] = g.url
        d['price'] = str(g.price)
        d['tags'] = g.get_tags()
        if sales:
            d['sales'] = {'total_sales' : str(g.purchase__fee__sum), 'times_bought' : g.purchase__count}
        if scores:
            key = 'highscores_top_' + str(scores) 
            d[key] = []
            for s in list(g.highscore_set.all())[:scores]:
                d[key].append({'time' : str(s.date_time), 'player' : s.player.username, 'score' : str(s.score)})                
        result['games'].append(d)        
        
    jsondata = dumps(result)
    try:
        function_name = request.GET['callback']
    except:
        pass
    else:
        jsondata = ''.join([function_name + '(', jsondata, ')'])

    
    return HttpResponse(jsondata, content_type='application/json')