# swagger_specs.py

submit_url_spec = {
    'tags': ['YouTube'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'youtube_url': {'type': 'string'}
                },
                'required': ['youtube_url']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Returns a job_id',
            'schema': {
                'type': 'object',
                'properties': {
                    'job_id': {'type': 'string'}
                }
            }
        }
    }
}

status_spec = {
    'tags': ['Job'],
    'parameters': [
        {
            'name': 'job_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Job ID to check status'
        }
    ],
    'responses': {
        200: {
            'description': 'Job status',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'}
                }
            }
        }
    }
}

chat_spec = {
    'tags': ['Chat'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'job_id': {'type': 'string'}
                },
                'required': ['message', 'job_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Chat response from transcript assistant',
            'schema': {
                'type': 'object',
                'properties': {
                    'reply': {'type': 'string'}
                }
            }
        }
    }
}
