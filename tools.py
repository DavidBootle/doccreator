from http import HTTPStatus # for status codes
from enum import Enum
import json

class Methods:

    GET: bool
    POST: bool

    def __init__(self, *args):

        calculated_args = []

        for index, arg in enumerate(args):
            calculated_args.append(str.lower(arg))
        
        self.GET = True if "get" in calculated_args else False
        self.POST = True if "post" in calculated_args else False

        if self.GET == False and self.POST == False:
            raise ValueError('Method cannot have no methods.')
    
    @classmethod
    def load(cls, obj):
        get = obj['GET']
        post = obj['POST']
        args = []
        if get:
            args.append('GET')
        if post:
            args.append('POST')
        return cls(*args)
    
    def __str__(self):
        if self.GET and self.POST:
            return "GET & POST"
        elif self.GET:
            return "GET"
        elif self.POST:
            return "POST"
    
    def getMethodList(self):
        methods = []
        if self.GET:
            methods.append('GET')
        if self.POST:
            methods.append('POST')
        return methods

    def getObject(self):
        return {
            'GET': self.GET,
            'POST': self.POST
        }

class Param:
    
    name: str
    value_type: str
    required: bool
    description: str
    default_value: str

    def __init__(self, name, value_type, required, description, default_value = None):
        self.name = name

        self.value_type = value_type

        if type(required) == bool:
            self.required = required
        else:
            raise ValueError("Argument required must be a bool")
        
        self.description = description
        
        self.default_value = default_value
    
    def __str__(self):
        return json.dumps(self.getObject())
    
    @classmethod
    def load(cls, obj):
        name = obj['name']
        value_type = obj['value_type']
        description = obj['description']
        required = obj['required']
        if required:
            default_value = None
        else:
            default_value = obj['default_value']
        return cls(name, value_type, required, description, default_value)
    
    def getObject(self):
        if self.required:
            return {
                'name': self.name,
                'value_type': self.value_type,
                'required': True,
                'description': self.description,
                'default_value': 'N/A'
            }
        else:
            return {
                'name': self.name,
                'value_type': self.value_type,
                'required': False,
                'description': self.description,
                'default_value': self.default_value
            }

class ContentType(Enum):
    JSON = 0

class PageLogic:
    
    steps: tuple[str]
    error_handling: str

    def __init__(self, steps, error_handling = None):
        self.steps = steps

        self.error_handling = error_handling
    
    def __str__(self):
        return json.dumps(self.getObject())
    
    @classmethod
    def load(cls, obj):
        steps = obj['steps']
        error_handling = obj['error_handling']
        return cls(steps, error_handling)
    
    def getObject(self):
        if self.error_handling:
            return {
                'steps': self.steps,
                'error_handling': self.error_handling
            }

class Response:
    
    method: str
    status_code: int
    status: str
    content: str
    context: str

    def __init__(self, method, status_code, content, context):

        method = str.upper(method)
        if method != 'GET' and method != 'POST':
            raise ValueError('Method must be either GET or POST')
        self.method = method

        self.status_code = status_code

        self.status = HTTPStatus(status_code).name

        self.content = content

        self.context = context
    
    def __str__(self):
        return json.dumps(self.getObject())
    
    @classmethod
    def load(cls, obj):
        method = obj['method']
        status_code = obj['status_code']
        content = obj['content']
        context = obj['context']
        return cls(method, status_code, content, context)

    def getObject(self):
        return {
            'method': self.method,
            'status_code': self.status_code,
            'status': self.status,
            'content': self.content,
            'context': self.context
        }

class Path:

    title: str
    path: str
    methods: Methods
    query_params: tuple[Param]
    request_params: tuple[Param]
    logic: tuple[PageLogic]
    responses: tuple[Response]
    requireAuth: bool
    requireMasterAuth: bool
    
    # things needed in a section about a path
    # paths (get and/or post)
    # Description (just add a title and placeholder)
    # if GET, then Query Parameters (optional)
    # if POST, then Request Parameters (optional)
    # logic (optional)
    # possible responses
    # if GET & POST, then create seperate paths for get and post

    def __init__(self, title, path, methods, responses, query_params = None, request_params = None, logic = None, requireAuth = False, requireMasterAuth = False):

        self.title = title
        self.path = path
        self.methods = methods
        self.responses = responses
        self.query_params = query_params
        self.request_params = request_params
        self.logic = logic
        self.requireAuth = requireAuth
        self.requireMasterAuth = requireMasterAuth
    
    def getObject(self):

        returnObj = {
            'title': self.title,
            'path': self.path,
            'methods': self.methods.getObject(),
            'requireAuth': self.requireAuth,
            'requireMasterAuth': self.requireMasterAuth
        }

        responsesList = []
        for response in self.responses:
            responsesList.append(response.getObject())
        returnObj['responses'] = responsesList

        if self.query_params:
            query_params_list = []
            for query_param in self.query_params:
                query_params_list.append(query_param.getObject())
            returnObj['query_params'] = query_params_list
        
        if self.request_params:
            request_params_list = []
            for request_param in self.request_params:
                request_params_list.append(request_param.getObject())
            returnObj['request_params'] = request_params_list
        
        if self.logic:
            returnObj['logic'] = self.logic.getObject()
        
        return returnObj
    
    def __str__(self):
        return json.dumps(self.getObject())
    
    def save(self, path):
        with open(path, 'w+') as f:
            f.write(json.dumps(self.getObject()))

    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            pathObject = json.loads(f.read())

        title = pathObject['title']
        path = pathObject['path']

        methods = Methods.load(pathObject['methods'])

        fResponses = pathObject['responses']
        responses = []
        for response in fResponses:
            responses.append(Response.load(response))
        
        if pathObject.get('query_params'):
            fQueryParams = pathObject['query_params']
            query_params = []
            for query_param in fQueryParams:
                query_params.append(Param.load(query_param))
        else:
            query_params = None
        
        if pathObject.get('request_params'):
            fRequestParams = pathObject['request_params']
            request_params = []
            for request_param in fRequestParams:
                request_params.append(RequestParam.load(request_param))
        else:
            request_params = None
    
        if pathObject.get('logic'):
            fLogic = pathObject['logic']
            logic = PageLogic.load(fLogic)
        else:
            logic = None
        
        requireAuth = pathObject['requireAuth']
        requireMasterAuth = pathObject['requireMasterAuth']

        return cls(title, path, methods, responses, query_params, request_params, logic, requireAuth, requireMasterAuth)
    
    def render(self, path):
        with open(path, 'w+') as f:
            f.write(f"## {self.title}\n")
            f.write("\n")
            f.write("| Title | Path | Method | Requires Authentication | Requires Master Authentication |\n")
            f.write("|---|---|---|---|---|\n")

            requireAuthSymbol = "✅" if self.requireAuth else "❌"
            requireMasterAuthSymbol = "✅" if self.requireMasterAuth else "❌"

            methodList = self.methods.getMethodList()
            for method in methodList:
                f.write(f"| [{self.title}]() | `{self.path}` | [{method}]() | {requireAuthSymbol} | {requireMasterAuthSymbol} |\n")
            f.write('\n')
            
            for method in methodList:
                if len(methodList) == 2:
                    f.write(f'### {method}\n')
                    f.write('\n')
            
                f.write('#### Description\n')
                f.write('\n')
                f.write('The description for the path goes here.\n')
                f.write('\n')

                if self.query_params != None:
                    f.write('#### Query Parameters\n')
                    f.write('| Name | Value Type | Required | Default Value | Description |\n')
                    f.write('|---|---|---|---|---|\n')
                    for param in self.query_params:
                        required = "✅" if param.required else "❌"
                        default = 'N/A' if param.required else f"`{param.default_value}`"
                        f.write(f'| `{param.name}` | `{param.value_type}` | {required} | {default} | {param.description} |\n')
                    f.write('\n')
                
                if self.request_params != None:
                    f.write('#### Request Parameters\n')
                    f.write('This path only accepts JSON data. When sending a request, the `Content-Type` header must be set to `application/json`, and the request body must be a JSON string that contains all the parameters listed below.\n')
                    f.write('\n')
                    f.write('| Name | Value Type | Required | Default Value | Description |\n')
                    f.write('|---|---|---|---|---|\n')
                    for param in self.query_params:
                        required = "✅" if param.required else "❌"
                        default = 'N/A' if param.required else f"`{param.default_value}`"
                        f.write(f'| `{param.name}` | `{param.value_type}` | {required} | {default} | {param.description} |\n')
                    f.write('\n')

                if self.logic != None:
                    f.write('#### Logic\n')
                    for index, line in enumerate(self.logic.steps):
                        f.write(f'{index + 1}. {line}\n')
                    if self.logic.error_handling != None:
                        f.write('\n')
                        f.write(self.logic.error_handling + '\n')
                    f.write('\n')

                f.write('#### Possible Responses\n')
                f.write('| Method | Status Code | Status | Content | Context |\n')
                f.write('|---|---|---|---|---|\n')
                for response in self.responses:
                    f.write(f'| {response.method} | {response.status_code} | {response.status} | {response.content} | {response.context} |\n')