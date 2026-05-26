
from questions.tasks import get_best_users, get_popular_tags


def sidebar_data(request):
    if request.path.startswith('/admin/') or request.path.startswith('/__debug__/'):
        return {}

    return {
        'popular_tags': get_popular_tags(),
        'top_users': get_best_users(),
    }