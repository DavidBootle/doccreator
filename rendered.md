## Teams

| Title | Path | Method | Requires Authentication | Requires Master Authentication |
|---|---|---|---|---|
| [Teams]() | `/teams` | [GET]() | ✅ | ❌ |

#### Description

The description for the path goes here.

#### Query Parameters
| Name | Value Type | Required | Default Value | Description |
|---|---|---|---|---|
| `confirm` | `bool` | ❌ | `true` | Controls whether to enable confirmation messages for deleting a team. Any value other than `false` will result in the default value `true` being used. |

#### Logic
1. Gets the confirmation variable from query parameters. If the query parameter is not set to `false`, then the value is set to `true`. Otherwise, the value is to `false`.
2. Get a list containing every team object from the database.
3. Render the code for the teams page behind the scenes.
4. Send the rendered html.

If an error occurs while executing this code, the page will instead render the error page and respond with a status of 500.

#### Possible Responses
| Method | Status Code | Status | Content | Context |
|---|---|---|---|---|
| GET | 200 | OK | HTML for the requested page | Normal operation |
| GET | 500 | INTERNAL_SERVER_ERROR | Error page | An error occurs when loading team data |
