# Guide d'Intégration .NET 8

## Configuration JWT

### 1. Installer le package NuGet

```bash
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
```

### 2. Configuration dans Program.cs

```csharp
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// JWT Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = "awana-auth-service",
            ValidAudience = "awana-auth-service",
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes("your-super-secret-key-min-32-chars"))
        };
    });

builder.Services.AddAuthorization();
builder.Services.AddControllers();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

### 3. appsettings.json

```json
{
  "Jwt": {
    "SecretKey": "your-super-secret-key-min-32-chars",
    "Issuer": "awana-auth-service",
    "Audience": "awana-auth-service"
  },
  "AuthService": {
    "BaseUrl": "http://localhost:8000"
  }
}
```

## Service d'Auth

### AuthService.cs

```csharp
public class AuthService
{
    private readonly HttpClient _httpClient;
    
    public AuthService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }
    
    public async Task<AuthResponse> LoginAsync(string username, string password)
    {
        var response = await _httpClient.PostAsJsonAsync(
            "/api/auth/local/login",
            new { username, password }
        );
        
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<AuthResponse>();
    }
    
    public async Task<AuthResponse> RefreshTokenAsync(string refreshToken)
    {
        var response = await _httpClient.PostAsJsonAsync(
            "/api/auth/refresh",
            new { refresh_token = refreshToken }
        );
        
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<AuthResponse>();
    }
}

public record AuthResponse(
    string access_token,
    string refresh_token,
    UserDto user
);

public record UserDto(
    string id,
    string email,
    List<string> roles
);
```

## Controllers

### SecureController.cs

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/[controller]")]
public class SecureController : ControllerBase
{
    [HttpGet]
    [Authorize]
    public IActionResult GetData()
    {
        var userId = User.FindFirst("sub")?.Value;
        var email = User.FindFirst("email")?.Value;
        var roles = User.FindAll("roles").Select(c => c.Value);
        
        return Ok(new { userId, email, roles });
    }
    
    [HttpGet("admin")]
    [Authorize(Roles = "admin")]
    public IActionResult GetAdminData()
    {
        return Ok(new { message = "Admin only" });
    }
}
```
