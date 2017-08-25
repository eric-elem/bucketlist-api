from flask import Blueprint, jsonify, request
from app.utils import token_required, get_json_input
from app.models import Bucketlist, Item, db

bucketlists = Blueprint('bucketlists', __name__)


@bucketlists.route('', methods=['POST', 'GET'])
@token_required
def bucketlists_view(the_user):
    """ Creates a bucketlist """
    if request.method == 'POST':
        new_bucketlist_json = get_json_input()
        if 'title' in new_bucketlist_json and 'description' in new_bucketlist_json:
            if len(new_bucketlist_json['title']) and len(new_bucketlist_json['description']):
                existing_bucketlist = Bucketlist.query.filter_by(title=new_bucketlist_json['title']).first()
                if not existing_bucketlist:
                    a_bucketlist = Bucketlist(new_bucketlist_json['title'], new_bucketlist_json['description'], the_user.user_id)
                    db.session.add(a_bucketlist)
                    db.session.commit()
                    response = {
                        'status' : 'Success',
                        'message' : 'Bucketlist ' + a_bucketlist.title + ' has been created',
                        'bucketlist' : {
                            'id' : a_bucketlist.bucketlist_id,
                            'title' : a_bucketlist.title,
                            'description' : a_bucketlist.description,
                            'created_at' : a_bucketlist.created_at
                        }
                    }
                    return jsonify(response), 201
                response = {
                    'status' : 'Error',
                    'message' : 'A bucketlist with the title ' + new_bucketlist_json['title'] + ' already exists'
                }
                return jsonify(response), 400
            response = {
                'status' : 'Error',
                'message' : 'Bucketlist title and/or description cannot be blank'
            }
            return jsonify(response), 400
        response = {
            'status' : 'Error',
            'message' : "Please provide a 'title' and 'description' for the new bucketlist"
        }
        return jsonify(response), 400
    if 'q' in request.args:
        title = request.args['q']
        searched_bucket = Bucketlist.query.filter_by(title=title).first()
        if searched_bucket:
            searched_bucket_dict = {
                'id' : searched_bucket.bucketlist_id,
                'title' : searched_bucket.title,
                'description' : searched_bucket.description,
                'created_at' : searched_bucket.created_at,
                'updated_at' : searched_bucket.updated_at
            }
            response = {
                'status' : 'Success',
                'message' : 'Bucket found',
                'bucket' : searched_bucket_dict
            }
            return jsonify(response), 200
        response = {
            'status' : 'Error',
            'message' : 'Bucket with title ' + title + ' not found'
        }
        return jsonify(response), 404

    bucketlists_objs = the_user.bucketlists
    if bucketlists_objs:
        bucketlist_limit = 0
        bucketlist_count = 0
        if 'limit' in request.args:
            try:
                bucketlist_limit = int(request.args['limit'])
            except ValueError:
                response = {
                    'status': 'Error',
                    'message': 'Limit should be a positive integer'
                }
                return jsonify(response), 404
        bucketlists_array = []
        for bucketlist_obj in bucketlists_objs:
            bucketlist_dict = {
                'id' : bucketlist_obj.bucketlist_id,
                'title' : bucketlist_obj.title,
                'description' : bucketlist_obj.description,
                'created_at' : bucketlist_obj.created_at,
                'updated_at' : bucketlist_obj.updated_at
            }
            bucketlists_array.append(bucketlist_dict)
            if bucketlist_limit > bucketlist_count:
                bucketlist_count += 1
                if bucketlist_limit == bucketlist_count:
                    break
        if len(bucketlists_array):
            response = {
                'status' : 'Success',
                'message' : 'Buckets found',
                'bucketlists' : bucketlists_array
            }
            return jsonify(response), 200
    response = {
        'status' : 'Success',
        'message' : 'Sorry, user ' + the_user.name + ' has no buckets'
    }
    return jsonify(response), 404


@bucketlists.route('/<identity>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def bucketlist(the_user, identity):
    """ Returns a bucketlist whose ID has been provided """
    the_bucketlist = Bucketlist.query.filter_by(bucketlist_id=identity).first()
    if the_bucketlist:
        if request.method == 'GET':
            obj = {
                'identity' : the_bucketlist.bucketlist_id,
                'title' : the_bucketlist.title,
                'description' : the_bucketlist.description,
                'created_at' : the_bucketlist.created_at,
                'updated_at' : the_bucketlist.updated_at
            }
            response = {
                'status': 'Success',
                'message': 'Bucketlist found',
                'bucketlist': obj
            }
            return jsonify(response), 200
        elif request.method == 'PUT':
            update_bucketlist_json = get_json_input()
            if 'title' in update_bucketlist_json or 'description' in update_bucketlist_json:
                if 'title' in update_bucketlist_json:
                    the_bucketlist.title = update_bucketlist_json['title']
                if 'description' in update_bucketlist_json:
                    the_bucketlist.description = update_bucketlist_json['description']
                db.session.commit()
                response = {
                    'status' : 'Success',
                    'message' : 'Bucketlist has been updated',
                    'bucketlist' : {
                        'id' : the_bucketlist.bucketlist_id,
                        'title' : the_bucketlist.title,
                        'description' : the_bucketlist.description,
                        'created_at' : the_bucketlist.created_at,
                        'updated_at' : the_bucketlist.updated_at
                    }
                }
                return jsonify(response), 200
            response = {
                'status' : 'Error',
                'message' : "Please provide a 'title' and/or 'description' for the bucketlist"
            }
            return jsonify(response), 400
        else:
            db.session.delete(the_bucketlist)
            db.session.commit()
            response = {
                'status' : 'Success',
                'message' : 'Bucketlist ' + the_bucketlist.title + ' with id ' + identity + ' deleted'
            }
            return jsonify(response), 200
    response = {
        'status' : 'Error',
        'message' : 'Bucketlist with id ' + identity + ' not found'
    }
    return jsonify(response), 404

@bucketlists.route('/<bucket_identity>/items', methods=['POST', 'GET'])
@token_required
def items(the_user, bucket_identity):
    """ Creates a new Item """
    curr_bucketlist = Bucketlist.query.filter_by(bucketlist_id=bucket_identity).first()
    if curr_bucketlist:
        if request.method == 'POST':
            new_item_json = get_json_input()
            if 'title' in new_item_json and 'description' in new_item_json:
                if len(new_item_json['title']) or len(new_item_json['description']):
                    existing_item = Item.query.filter_by(
                        title=new_item_json['title']).first()
                    if not existing_item:
                        new_item = Item(new_item_json['title'], new_item_json['description'], bucket_identity)
                        db.session.add(new_item)
                        db.session.commit()
                        response = {
                            'status' : 'Success',
                            'message' : 'Item has been created',
                            'item' : {
                                'id' : new_item.item_id,
                                'title' : new_item.title,
                                'description' : new_item.description,
                                'created_at' : new_item.created_at
                            }
                        }
                        return jsonify(response), 201
                    response = {
                        'status' : 'Error',
                        'message' : 'An item with the title ' + existing_item.title + ' already exists'
                    }
                    return jsonify(response), 404
                response = {
                    'status' : 'Error',
                    'message' : 'Item title and/or description cannot be blank'
                }
                return jsonify(response), 400
            response = {
                'status' : 'Error',
                'message' : 'Please provide a title and description for the new item'
            }
            return jsonify(response), 400
        
        if 'q' in request.args:
            title = request.args['q']
            searched_item = Item.query.filter_by(title=title).first()
            if searched_item:
                searched_item_dict = {
                    'id' : searched_item.item_id,
                    'title' : searched_item.title,
                    'description' : searched_item.description,
                    'status' :searched_item.status,
                    'created_at' : searched_item.created_at,
                    'updated_at' : searched_item.updated_at
                }
                response = {
                    'status': 'Success',
                    'message': 'Item found',
                    'item': searched_item_dict
                }
                return jsonify(response), 200
            response = {
                'status' : 'Error',
                'message' : 'Item with title ' + title + ' not found'
            }
            return jsonify(response), 404

        item_objs = curr_bucketlist.items
        if item_objs:
            items_limit = 0
            items_count = 0
            if 'limit' in request.args:
                try:
                    items_limit = int(request.args['limit'])
                except ValueError:
                    response = {
                        'status': 'Error',
                        'message': 'Limit should be a positive integer'
                    }
                    return jsonify(response), 404
            items_array = []
            for item_obj in item_objs:
                item_dict = {
                    'id' : item_obj.item_id,
                    'title' : item_obj.title,
                    'description' : item_obj.description,
                    'status' : item_obj.status,
                    'created_at' : item_obj.created_at,
                    'updated_at' : item_obj.updated_at
                }
                items_array.append(item_dict)
                if items_limit > items_count:
                    items_count += 1
                    if items_limit == items_count:
                        break
            if len(items_array):
                response = {
                    'status' : 'Success',
                    'message' : 'Items found in bucketlist ' + curr_bucketlist.title,
                    'items' : items_array
                }
                return jsonify(response), 200
        response = {
            'status' : 'Error',
            'message' : 'No items found in bucketlist ' + curr_bucketlist.title
        }
        return jsonify(response), 404
    response = {
        'status' : 'Error',
        'message' : 'Bucketlist with id ' + bucket_identity + ' not found'
    }
    return jsonify(response), 404

@bucketlists.route('/<bucket_identity>/items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def item(the_user, bucket_identity, item_id):
    """ Updates or deletes an Item """
    wor_bucketlist = Bucketlist.query.filter_by(bucketlist_id=bucket_identity).first()
    if wor_bucketlist:
        cur_item = Item.query.filter_by(item_id=item_id).first()
        if cur_item:
            if request.method == 'PUT':
                updt_item_json = get_json_input()
                if 'title' in updt_item_json or 'description' in updt_item_json or 'new_status' in updt_item_json:
                    if 'title' in updt_item_json:
                        cur_item.title = updt_item_json['title']
                    if 'description' in updt_item_json:
                        cur_item.description = updt_item_json['description']
                    if 'new_status' in updt_item_json:
                        cur_item.status = updt_item_json['new_status']
                    db.session.commit()
                    response = {
                        'status' : 'Success',
                        'message' : 'Item updated',
                        'item' : {
                            'id' : cur_item.item_id,
                            'title' : cur_item.title,
                            'description' : cur_item.description,
                            'status' : cur_item.status,
                            'created_at' : cur_item.created_at,
                            'updated_at' : cur_item.updated_at
                        }
                    }
                    return jsonify(response), 200
                response = {
                    'status' : 'Error',
                    'message' : 'Please provided a new_title, new_description and/or new_status for the item'
                }
                return jsonify(response), 400

            db.session.delete(cur_item)
            db.session.commit()
            response = {
                'status' : 'Success',
                'message' : 'Item ' + cur_item.title + ' with id ' + item_id + ' deleted'
            }
            return jsonify(response), 200
        response = {
            'status' : 'Error',
            'message' : 'Item with id ' + item_id + ' not found'
        }
        return jsonify(response), 404
    response = {
        'status' : 'Error',
        'message' : 'Bucketlist with id ' + bucket_identity + ' not found'
    }
    return jsonify(response), 404


@bucketlists.errorhandler(404)
def handle_error_404(error):
    response = {
        'status' : 'Error',
        'message' : 'Request not found'
    }
    return jsonify(response), 404
