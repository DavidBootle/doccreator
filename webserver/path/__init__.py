from enum import Enum
from http import HTTPStatus
import json
import re

class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def obj(self) -> str:
        return self.name
    
    @classmethod
    def load(cls, obj):
        return cls(obj)

class HTTPPath:
    url: str
    _method: HTTPMethod
    requireAuth: bool
    requireMasterAuth: bool

    def __init__(self, url: str, method: HTTPMethod = HTTPMethod.GET, requireAuth: bool = False, requireMasterAuth: bool = False):
        self.url = url
        self.method = method
        self.requireAuth = requireAuth
        self.requireMasterAuth = requireMasterAuth
    
    @property
    def method(self):
        return self._method
    
    @method.setter
    def method(self, value):
        if type(value) == HTTPMethod:
            self._method = value
        else:
            self._method = HTTPMethod(value)
    
    def __repr__(self) -> str:
        # <HTTPPath: "/teams" via GET>
        return f'<HTTPPath: "{self.url}" via {self.method}>'
    
    def __str__(self) -> str:
        return f'"{self.url}" via {self.method}'
    
    @property
    def obj(self) -> dict:
        return {
            'url': self.url,
            'method': self.method.obj,
            'requireAuth': self.requireAuth,
            'requireMasterAuth': self.requireMasterAuth
        }
    
    @classmethod
    def load(cls, obj):
        requireAuth = obj['requireAuth']
        requireMasterAuth = obj['requireMasterAuth']
        return cls(obj['url'], HTTPMethod.load(obj['method']), requireAuth, requireMasterAuth)

class Parameter:
    name: str
    value_type: str
    required: bool
    default: str
    description: str

    def __init__(self, name: str = '', value_type: str = 'null', required: bool = False, default: str = None, description = None):
        self.name = name
        self.value_type = value_type
        self.required = required
        self.default = default
        self.description = description
    
    def __repr__(self) -> str:
        # <Parameter: test>
        return f'<Parameter: {self.name}>'
    
    def __str__(self) -> str:
        # (optional/required) parameter 'test'
        if self.required:
            return f'required parameter "{self.name}"'
        else:
            return f'optional parameter "{self.name}"'
    
    @property
    def obj(self) -> dict:
        obj = {
            'name': self.name,
            'value_type': self.value_type,
            'required': self.required
        }

        if not self.required:
            obj['default'] = self.default
        
        if self.description != None:
            obj['description'] = self.description
        return obj
    
    @classmethod
    def load(cls, obj):
        name = obj['name']
        value_type = obj['value_type']
        required = obj['required']
        default = obj.get('default', None)
        description = obj.get('description', None)
        return cls(name, value_type, required, default, description)

class CustomIterator:

    def __init__(self, reference):
        self._reference = reference
        self._index = 0
    
    def __next__(self):
        if self._index >= len(self._reference): raise StopIteration
        result = self._reference[self._index]
        self._index += 1
        return result

class Parameters:
    _parameters: list[Parameter]
    notes: str

    def __init__(self, parameters: list[Parameter] = [], notes: str = None):
        self.parameters = parameters
        self.notes = notes
    
    @property
    def parameters(self):
        return self._parameters
    
    @parameters.setter
    def parameters(self, value):
        if type(value) != list:
            self._parameters = [value]
        else:
            self._parameters = value
    
    def __getitem__(self, key):
        if type(key) != int: raise TypeError
        return self.parameters[key]
    
    def __setitem__(self, key, value):
        if type(key) != int: raise TypeError
        if type(value) != Parameter: raise TypeError
        self.parameters[key] = value
    
    def __repr__(self) -> str:
        # <Parameters: [<Parameter: test>]>
        # <Parameters: [<Parameter: test>, notes: "Test"]>
        if self.notes == None:
            return f'<Parameters: {repr(self.parameters)}>'
        else:
            return f'<Parameters: {repr(self.parameters)[:-1]}, notes: "{self.notes}"]>'
    
    def __str__(self) -> str:
        # [<Parameter: test>]
        # [<Parameter: test>, notes: "Test"]
        if self.notes == None:
            return repr(self.parameters)
        else:
            return f'{repr(self.parameters)[:-1]}, notes: "{self.notes}"]'
    
    def __iter__(self):
        return CustomIterator(self)
    
    def __len__(self):
        return len(self.parameters)
    
    def add(self, *parameters):
        for parameter in parameters:
            self.parameters.append(parameter)
    
    @property
    def obj(self) -> dict:
        parameters = []
        for parameter in self.parameters:
            parameters.append(parameter.obj)
        obj = {
            'parameters': parameters
        }
        if self.notes != None:
            obj['notes'] = self.notes
        return obj
    
    @classmethod
    def load(cls, obj):
        parameters = obj['parameters']
        loaded_parameters = []
        for parameter in parameters:
            loaded_parameters.append(Parameter.load(parameter))

        notes = obj.get('notes', None)

        return Parameters(loaded_parameters, notes)

class Response:
    _status: HTTPStatus
    content: str
    context: str

    def __init__(self, status = HTTPStatus.OK, content = None, context = None):
        self.status = status
        self.content = content
        self.context = context
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        if type(value) == HTTPStatus:
            self._status = value
        elif type(value) == int:
            self._status = HTTPStatus(value)
        else:
            self._status = HTTPStatus[value]
    
    @property
    def status_code(self) -> int:
        return self.status.value
    
    @property
    def status_string(self) -> str:
        return self.status.name
    
    def __repr__(self):
        # <Response: 500 INTERNAL_SERVER_ERROR>
        return f'<Response: {self.status_code} {self.status_string}>'
    
    def __str__(self):
        # 500 INTERNAL_SERVER_ERROR
        return f'{self.status_code} {self.status_string}'
    
    @property
    def obj(self) -> dict:
        obj = {
            'status': self.status_code
        }
        if self.content != None:
            obj['content'] = self.content
        if self.context != None:
            obj['context'] = self.context
        return obj
    
    @classmethod
    def load(cls, obj):
        status = obj['status']
        content = obj.get('content', None)
        context = obj.get('context', None)
        return Response(status, content, context)

class Logic:
    _steps: list[str]
    notes: str

    def __init__(self, steps = [], notes = None):
        self.steps = steps
        self.notes = notes
    
    @property
    def steps(self):
        return self._steps
    
    @steps.setter
    def steps(self, value):
        if type(value) == str:
            self._steps = [value]
        else:
            self._steps = value

    def __getitem__(self, key):
        if type(key) != int: raise TypeError
        return self.steps[key]
    
    def __setitem__(self, key, value):
        if type(key) != int: raise TypeError
        self.steps[key] = value
    
    def __len__(self):
        return len(self.steps)
    
    def __iter__(self):
        return CustomIterator(self)
    
    def add(self, *args: str):
        for arg in args:
            self.steps.append(arg)
    
    @property
    def obj(self):
        obj = {
            'steps': self.steps
        }
        if self.notes != None:
            obj['notes'] = self.notes
        return obj
    
    @classmethod
    def load(cls, obj):
        steps = obj['steps']
        notes = obj.get('notes', None)
        return cls(steps, notes)

class Subsection:
    path: HTTPPath
    parameters: Parameters
    logic: Logic
    responses: list[Response]
    _description: str

    def __init__(self, path: HTTPPath = HTTPPath(''), parameters: Parameters = None, logic: Logic = None, responses: list[Response] = [], description: str = None):
        self.path = path
        self.parameters = parameters
        self.logic = logic
        self.responses = responses
        self.description = description
    
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if type(value) == str:
            description = re.sub(r"^\n*", '', value) # remove any newlines at the start of the description
            description = re.sub(r"\n*$", '', description) # remove any newlines at the end of the description
            description = re.sub(r"(?<!\n)\n(?!\n)", ' ', description) # remove lone \n
            self._description = description
        else:
            self._description = value

    @property
    def obj(self):
        obj = {
            'path': self.path.obj
        }
        if self.parameters != None:
            obj['parameters'] = self.parameters.obj
        if self.logic != None:
            obj['logic'] = self.logic.obj
        if self.description != None:
            obj['description'] = self.description
        responses = []
        for response in self.responses:
            responses.append(response.obj)
        obj['responses'] = responses
        return obj
    
    @classmethod
    def load(cls, obj):
        path = HTTPPath.load(obj['path'])
        parameters = obj.get('parameters', None)
        if parameters != None:
            parameters = Parameters.load(parameters)
        logic = obj.get('logic', None)
        if logic != None:
            logic = Logic.load(logic)
        responses = obj.get('responses', None)
        calculated_responses = []
        for response in responses:
            calculated_responses.append(Response.load(response))
        responses = calculated_responses
        description = obj.get('description', None)
        return cls(path, parameters, logic, responses, description)

class Section:
    title: str
    _subsections: list[Subsection]

    def __init__(self, title: str = 'Untitled', subsections = []):
        self.title = title
        self.subsections = subsections
    
    @property
    def subsections(self):
        return self._subsections
    
    @subsections.setter
    def subsections(self, value):
        if type(value) != list:
            self._subsections = [value]
        else:
            self._subsections = value
    
    def __getitem__(self, index):
        if type(index) != int: raise TypeError
        return self.subsections[index]
    
    def __setitem__(self, index, value):
        if type(index) != int: raise TypeError
        self.subsections[index] = value
    
    def __len__(self):
        return len(self.subsections)
    
    def __iter__(self):
        return CustomIterator(self)
    
    @property
    def obj(self):
        obj = {
            'title': self.title
        }
        subsections = []
        for subsection in self.subsections:
            subsections.append(subsection.obj)
        obj['subsections'] = subsections
        return obj
    
    @classmethod
    def load(cls, obj):
        title = obj['title']
        subsections = obj['subsections']
        calculated_subsections = []
        for subsection in subsections:
            calculated_subsections.append(Subsection.load(subsection))
        subsections = calculated_subsections
        return cls(title, subsections)
    
    def save(self, path):
        with open(path, 'w+') as f:
            f.write(json.dumps(self.obj))
    
    @classmethod
    def load_file(cls, path):
        with open(path, 'r') as f:
            data = json.loads(f.read())
            return cls.load(data)
    
    def render(self, path):
        with open(path, 'w+') as f:
            f.write(f"## {self.title}\n")
            f.write("\n")
            f.write("| Title | Path | Method | Requires Authentication | Requires Master Authentication |\n")
            f.write("|---|---|---|---|---|\n")
            for s in self: # s = subsection
                requireAuthSymbol = "✅" if s.path.requireAuth else "❌"
                requireMasterAuthSymbol = "✅" if s.path.requireMasterAuth else "❌"
                f.write(f"| [{self.title}]() | `{s.path.url}` | [{s.path.method}]() | {requireAuthSymbol} | {requireMasterAuthSymbol} |\n")
            f.write('\n')

            for s in self: # s = subsection
                if len(self) > 1:
                    f.write(f'### {s.path.method}\n')
                    f.write('\n')
                
                f.write('#### Description\n')
                f.write('\n')
                if s.description != None:
                    f.write(s.description)
                else:
                    f.write('Description for the subsection goes here.')
                f.write('\n')

                if s.parameters != None and s.path.method == HTTPMethod.GET: # if parameters are set and method is GET
                    f.write('#### Query Parameters\n')
                    f.write('| Name | Value Type | Required | Default Value | Description |\n')
                    f.write('|---|---|---|---|---|\n')
                
                if s.parameters != None and s.path.method == HTTPMethod.POST: # if parameters are set and method is POST
                    f.write('#### Request Parameters\n')
                    f.write('This path only accepts JSON data. When sending a request, the `Content-Type` header must be set to `application/json`, and the request body must be a JSON string that contains all the parameters listed below.\n')
                    f.write('\n')
                    f.write('| Name | Value Type | Required | Default Value | Description |\n')
                    f.write('|---|---|---|---|---|\n')
                
                if s.parameters != None:
                    for param in s.parameters:
                        required = "✅" if param.required else "❌"
                        default = 'N/A' if param.required else f"`{param.default}`"
                        f.write(f'| `{param.name}` | `{param.value_type}` | {required} | {default} | {param.description if param.description != None else "No description."} |\n')
                    f.write('\n')
                
                if s.logic != None:
                    f.write('#### Logic\n')
                    for index, line in enumerate(s.logic):
                        f.write(f'{index + 1}. {line}\n')
                    if s.logic.notes != None:
                        f.write('\n')
                        f.write(s.logic.notes + '\n')
                    f.write('\n')

                f.write('#### Possible Responses\n')
                f.write('| Method | Status Code | Status | Content | Context |\n')
                f.write('|---|---|---|---|---|\n')
                for response in s.responses:
                    f.write(f'| {s.path.method} | {response.status_code} | {response.status_string} | {response.content if response.content != None else "No content"} | {response.context if response.context != None else "No context"} |\n')