import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

from DjanGIUnchained import models
# Create your views here.
from DjanGIUnchained.decorators import cross_origin, returns_json, with_session


@cross_origin
@returns_json
@with_session
def all_piece_types(request, user: models.User):
    """
        The mighty power of the request that requests all the piece types
    :param user: the logged user to check if he can do some requests
    :param request: literally the request
    :return: all objects serialized as a JSON with a HTTP response
    """
    query_repsonse = models.PieceType.objects.all()
    dicted_response = [i.to_dict() for i in query_repsonse]
    return dicted_response


@cross_origin
@returns_json
@with_session
def all_pieces_from_this_type(request, user: models.User):
    """
        The mighty power of the request that requests all the piece types
    :param user: the logged user to check if he can do some requests
    :param request: literally the request
    :return: all objects serialized as a JSON with a HTTP response
    """
    if user.is_guest:
        return []
    piece_type_pk = None
    if request.method == 'GET' and 'id' in request.GET:
        piece_type_pk = request.GET['id']
    if piece_type_pk is not None:
        query_repsonse = models.Pieces.objects.filter(type_id=piece_type_pk)
        dicted_response = [i.to_dict() for i in query_repsonse]
        return dicted_response
    else:
        error_str = {'error': 'BAD REQUEST: It is required to receive an id as argument as follows '
                              '127.0.0.1:8000/pieces_from_type?id=[a-zA-Z]'}
        return HttpResponseBadRequest(json.dumps(error_str))


@cross_origin
@returns_json
@with_session
def piece_data(request, user: models.User):
    """
        The mighty power of the request that requests all the piece types
    :param user: the logged user to check if he can do some requests
    :param request: literally the request
    :return: all objects serialized as a JSON with a HTTP response
    """
    if user.is_guest:
        return []
    piece_id = None
    if request.method == 'GET' and 'id' in request.GET:
        piece_id = request.GET['id']
    if piece_id is not None:
        query_repsonse = models.Pieces.objects.filter(id=piece_id)
        dicted_response = [i.to_dict() for i in query_repsonse]
        return dicted_response
    else:
        error_str = {'error': 'BAD REQUEST: It is required to receive an id as argument as follows '
                              '127.0.0.1:8000/pieces_from_type?id=[a-zA-Z]'}
        return HttpResponseBadRequest(json.dumps(error_str))


@csrf_exempt
@cross_origin
@returns_json
@with_session
def new_piece(request, user: models.User):
    """
        Receives a request to create a new piece
    :param user: the logged user to check if he can do some requests
    :param request: http request
    :return: returns the new piece as json
    """
    if request.method == 'POST':
        if not user.is_admin:
            return HttpResponseBadRequest(json.dumps({'error': 'Not allowed to do that'}))
        piece_dict = json.loads(request.body)
        piece_type = models.PieceType.objects.filter(type_id=piece_dict['type_id'])
        if len(piece_type) == 0:
            return json.dumps({'error': 'That piece type does not exist'})
        new_piece_from_request = models.Pieces(name=piece_dict['name'], manufacturer=piece_dict['manufacturer'],
                                               type_id=piece_type[0])
        new_piece_from_request.save()
        return new_piece_from_request.to_dict()
    else:
        return HttpResponseBadRequest(json.dumps({'error': 'Bad Request LOL'}))


@csrf_exempt
@cross_origin
@returns_json
def login(request):
    if request.method == 'POST':
        request_dict = json.loads(request.body)
        user = models.User.objects.filter(name=request_dict['name'], password=request_dict['password'])
        if len(user) == 1:
            user_role_name = models.User.objects.get(name=request_dict['name']).roleName
            return {'token': request_dict['name'], 'role': user_role_name.to_dict()}
        else:
            return HttpResponseBadRequest(json.dumps({'error': 'WRONG COMBINATION'}))
    else:
        return HttpResponseBadRequest(json.dumps({'error': 'Bad Request LOL'}))


@csrf_exempt
@cross_origin
@returns_json
@with_session
def delete_piece(request, user: models.User):
    """
        Deletes a piece from the DB
    :param request: the request
    :param user: the logged user
    :return: si se ha borrado o no
    """
    if request.method == 'DELETE' and 'id' in request.GET:
        if not user.is_admin:
            return HttpResponseBadRequest(json.dumps({'error': 'You have not permission'}))
        piece_id = request.GET['id']
        models.Pieces.objects.filter(id=piece_id).delete()
        return json.dumps({'ok': 'process done'})
    else:
        return HttpResponseBadRequest(json.dumps({"error": "No id in delete request"}))


@csrf_exempt
@cross_origin
@returns_json
@with_session
def modify_piece(request, user: models.User):
    """
        Modifies a pieces from DB
    :param request: the request
    :param user: the logged user
    :return: return the modofied object
    """
    if request.method == 'POST':
        if not user.is_admin:
            return HttpResponseBadRequest(json.dumps({'error', 'Not allowed to do that'}))
        piece_dict = json.loads(request.body)
        piece_to_modify = models.Pieces.objects.filter(id=piece_dict['id'])
        if len(piece_to_modify) == 0:
            return HttpResponseBadRequest(json.dumps({'error': 'No piece found'}))
        manufacturer = piece_dict['manufacturer']
        if piece_to_modify[0].manufacturer != manufacturer and len(manufacturer) != 0:
            piece_to_modify[0].manufacturer = manufacturer
        name = piece_dict['name']
        if piece_to_modify[0].name != name and len(name) != 0:
            piece_to_modify[0].name = name
        piece_to_modify[0].save()
        return piece_to_modify[0].to_dict()
    else:
        return HttpResponseBadRequest(json.dumps({'error': 'Bad Request LOL'}))
