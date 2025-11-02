# Guide de Migration vers .NET 8 + PostgreSQL

## 🎯 Objectif

Ce document décrit comment migrer l'application JLC actuelle (FastAPI + MongoDB) vers l'architecture cible **.NET 8 + PostgreSQL** spécifiée dans le cahier des charges.

## 📚 Stack Cible

### Backend
- **.NET 8** (ASP.NET Core Web API)
- **Clean Architecture** (Domain / Application / Infrastructure / Presentation)
- **Entity Framework Core** pour PostgreSQL
- **FluentValidation** pour la validation
- **AutoMapper** pour les mappings
- **Serilog** pour les logs
- **MediatR** (optionnel) pour CQRS

### Frontend
- **React 18** avec TypeScript (conservé)
- **Redux Toolkit** (conservé)
- Architecture identique au frontend actuel

### Database
- **PostgreSQL 15+**
- Migrations via EF Core Migrations

## 📁 Structure Monorepo .NET

```
jlc-monorepo/
├── apps/
│   ├── api/                     # .NET 8 Web API
│   │   ├── src/
│   │   │   ├── Jlc.Api/            # Presentation Layer (Controllers, Middleware)
│   │   │   ├── Jlc.Application/    # Application Layer (Use Cases, DTOs, Validators)
│   │   │   ├── Jlc.Domain/         # Domain Layer (Entities, Value Objects, Events)
│   │   │   └── Jlc.Infrastructure/ # Infrastructure Layer (EF Core, Repos, Services)
│   │   └── tests/
│   │       ├── Jlc.Domain.Tests/
│   │       └── Jlc.Application.Tests/
│   └── web/                     # React (identique à l'actuel)
├── packages/
│   ├── ui/
│   └── types/
└── docker/
    └── docker-compose.yml
```

## 🔧 Étapes de Migration

### 1. Création de la Solution .NET

```bash
# Créer la solution
dotnet new sln -n Jlc

# Créer les projets
dotnet new webapi -n Jlc.Api -o apps/api/src/Jlc.Api
dotnet new classlib -n Jlc.Application -o apps/api/src/Jlc.Application
dotnet new classlib -n Jlc.Domain -o apps/api/src/Jlc.Domain
dotnet new classlib -n Jlc.Infrastructure -o apps/api/src/Jlc.Infrastructure

# Tests
dotnet new xunit -n Jlc.Domain.Tests -o apps/api/tests/Jlc.Domain.Tests
dotnet new xunit -n Jlc.Application.Tests -o apps/api/tests/Jlc.Application.Tests

# Ajouter les projets à la solution
dotnet sln add apps/api/src/Jlc.Api/Jlc.Api.csproj
dotnet sln add apps/api/src/Jlc.Application/Jlc.Application.csproj
dotnet sln add apps/api/src/Jlc.Domain/Jlc.Domain.csproj
dotnet sln add apps/api/src/Jlc.Infrastructure/Jlc.Infrastructure.csproj
dotnet sln add apps/api/tests/Jlc.Domain.Tests/Jlc.Domain.Tests.csproj
dotnet sln add apps/api/tests/Jlc.Application.Tests/Jlc.Application.Tests.csproj

# Références entre projets
cd apps/api/src/Jlc.Api
dotnet add reference ../Jlc.Application/Jlc.Application.csproj
dotnet add reference ../Jlc.Infrastructure/Jlc.Infrastructure.csproj

cd ../Jlc.Application
dotnet add reference ../Jlc.Domain/Jlc.Domain.csproj

cd ../Jlc.Infrastructure
dotnet add reference ../Jlc.Domain/Jlc.Domain.csproj
dotnet add reference ../Jlc.Application/Jlc.Application.csproj
```

### 2. Installation des Packages NuGet

```bash
# Jlc.Api
cd apps/api/src/Jlc.Api
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
dotnet add package Swashbuckle.AspNetCore
dotnet add package Serilog.AspNetCore

# Jlc.Application
cd ../Jlc.Application
dotnet add package FluentValidation
dotnet add package FluentValidation.DependencyInjectionExtensions
dotnet add package AutoMapper
dotnet add package AutoMapper.Extensions.Microsoft.DependencyInjection
dotnet add package MediatR

# Jlc.Infrastructure
cd ../Jlc.Infrastructure
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Microsoft.Extensions.Configuration
```

### 3. Modèles de Données (.NET)

#### Domain/Entities/Profile.cs

```csharp
namespace Jlc.Domain.Entities;

public enum ProfileType
{
    Admin,
    Agency,
    Company,
    Interim
}

public class Profile
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public ProfileType ProfileType { get; set; }
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? Phone { get; set; }
    public string? AvatarUrl { get; set; }
    
    // Extended data (JSON ou tables séparées)
    public AgencyProfile? AgencyData { get; set; }
    public CompanyProfile? CompanyData { get; set; }
    public InterimProfile? InterimData { get; set; }
    
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation
    public User User { get; set; } = null!;
}

public class AgencyProfile
{
    public string? AgencyName { get; set; }
    public string? AgencyCode { get; set; }
    public string? Address { get; set; }
    public string? Description { get; set; }
}

public class CompanyProfile
{
    public string? CompanyName { get; set; }
    public string? RegistrationNumber { get; set; }
    public string? Address { get; set; }
    public string? Industry { get; set; }
    public string? CompanySize { get; set; }
    public string? Website { get; set; }
}

public class InterimProfile
{
    public List<string> Skills { get; set; } = new();
    public int? ExperienceYears { get; set; }
    public string? ResumeUrl { get; set; }
    public string? Availability { get; set; }
    public string? Bio { get; set; }
    public List<string> Certifications { get; set; } = new();
}
```

#### Domain/Entities/AccountValidation.cs

```csharp
namespace Jlc.Domain.Entities;

public enum ValidationType
{
    Company,
    Interim
}

public enum ValidationStatus
{
    Pending,
    Approved,
    Rejected
}

public class AccountValidation
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string? UserEmail { get; set; }
    public string? UserName { get; set; }
    public ValidationType ValidationType { get; set; }
    public ValidationStatus Status { get; set; }
    public string? Comment { get; set; }
    public Guid? ReviewedBy { get; set; }
    public string? ReviewedByEmail { get; set; }
    public DateTime? ReviewedAt { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation
    public User User { get; set; } = null!;
}
```

### 4. DbContext et Configurations

#### Infrastructure/Data/JlcDbContext.cs

```csharp
using Microsoft.EntityFrameworkCore;
using Jlc.Domain.Entities;

namespace Jlc.Infrastructure.Data;

public class JlcDbContext : DbContext
{
    public JlcDbContext(DbContextOptions<JlcDbContext> options) : base(options)
    {
    }

    public DbSet<Profile> Profiles { get; set; }
    public DbSet<AccountValidation> AccountValidations { get; set; }
    public DbSet<Notification> Notifications { get; set; }
    public DbSet<AuditTrail> AuditTrails { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Profile Configuration
        modelBuilder.Entity<Profile>(entity =>
        {
            entity.ToTable("profiles");
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.UserId).IsUnique();
            
            // JSON columns pour les données étendues
            entity.OwnsOne(e => e.AgencyData, owned => owned.ToJson());
            entity.OwnsOne(e => e.CompanyData, owned => owned.ToJson());
            entity.OwnsOne(e => e.InterimData, owned => owned.ToJson());
        });

        // AccountValidation Configuration
        modelBuilder.Entity<AccountValidation>(entity =>
        {
            entity.ToTable("account_validations");
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.UserId);
            entity.HasIndex(e => e.Status);
        });

        // Notification Configuration
        modelBuilder.Entity<Notification>(entity =>
        {
            entity.ToTable("notifications");
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => new { e.UserId, e.IsRead });
        });

        // AuditTrail Configuration
        modelBuilder.Entity<AuditTrail>(entity =>
        {
            entity.ToTable("audit_trails");
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.EntityId);
            entity.HasIndex(e => e.UserId);
        });
    }
}
```

### 5. Migrations EF Core

```bash
# Installer EF Core tools
dotnet tool install --global dotnet-ef

# Créer la première migration
cd apps/api/src/Jlc.Infrastructure
dotnet ef migrations add InitialCreate --startup-project ../Jlc.Api/Jlc.Api.csproj

# Appliquer la migration
dotnet ef database update --startup-project ../Jlc.Api/Jlc.Api.csproj
```

### 6. Repositories

#### Infrastructure/Repositories/ProfileRepository.cs

```csharp
using Microsoft.EntityFrameworkCore;
using Jlc.Domain.Entities;
using Jlc.Infrastructure.Data;

namespace Jlc.Infrastructure.Repositories;

public interface IProfileRepository
{
    Task<Profile?> GetByUserIdAsync(Guid userId);
    Task<Profile?> GetByIdAsync(Guid id);
    Task<Profile> CreateAsync(Profile profile);
    Task<Profile> UpdateAsync(Profile profile);
    Task DeleteAsync(Guid id);
}

public class ProfileRepository : IProfileRepository
{
    private readonly JlcDbContext _context;

    public ProfileRepository(JlcDbContext context)
    {
        _context = context;
    }

    public async Task<Profile?> GetByUserIdAsync(Guid userId)
    {
        return await _context.Profiles
            .FirstOrDefaultAsync(p => p.UserId == userId);
    }

    public async Task<Profile?> GetByIdAsync(Guid id)
    {
        return await _context.Profiles.FindAsync(id);
    }

    public async Task<Profile> CreateAsync(Profile profile)
    {
        _context.Profiles.Add(profile);
        await _context.SaveChangesAsync();
        return profile;
    }

    public async Task<Profile> UpdateAsync(Profile profile)
    {
        profile.UpdatedAt = DateTime.UtcNow;
        _context.Profiles.Update(profile);
        await _context.SaveChangesAsync();
        return profile;
    }

    public async Task DeleteAsync(Guid id)
    {
        var profile = await _context.Profiles.FindAsync(id);
        if (profile != null)
        {
            _context.Profiles.Remove(profile);
            await _context.SaveChangesAsync();
        }
    }
}
```

### 7. Application Layer (DTOs, Use Cases)

#### Application/Profiles/Commands/UpdateProfileCommand.cs

```csharp
using MediatR;
using Jlc.Domain.Entities;

namespace Jlc.Application.Profiles.Commands;

public record UpdateProfileCommand : IRequest<ProfileDto>
{
    public Guid UserId { get; init; }
    public string? FirstName { get; init; }
    public string? LastName { get; init; }
    public string? Phone { get; init; }
    // ... autres champs
}

public class UpdateProfileCommandHandler : IRequestHandler<UpdateProfileCommand, ProfileDto>
{
    private readonly IProfileRepository _repository;
    private readonly IMapper _mapper;

    public UpdateProfileCommandHandler(IProfileRepository repository, IMapper mapper)
    {
        _repository = repository;
        _mapper = mapper;
    }

    public async Task<ProfileDto> Handle(UpdateProfileCommand request, CancellationToken cancellationToken)
    {
        var profile = await _repository.GetByUserIdAsync(request.UserId)
            ?? throw new NotFoundException("Profile not found");

        // Update fields
        profile.FirstName = request.FirstName;
        profile.LastName = request.LastName;
        profile.Phone = request.Phone;

        var updated = await _repository.UpdateAsync(profile);
        return _mapper.Map<ProfileDto>(updated);
    }
}
```

### 8. Controllers (Presentation)

#### Api/Controllers/ProfilesController.cs

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MediatR;
using Jlc.Application.Profiles.Commands;
using Jlc.Application.Profiles.Queries;

namespace Jlc.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ProfilesController : ControllerBase
{
    private readonly IMediator _mediator;

    public ProfilesController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("me")]
    public async Task<ActionResult<ProfileDto>> GetMyProfile()
    {
        var userId = GetCurrentUserId();
        var query = new GetProfileQuery { UserId = userId };
        var profile = await _mediator.Send(query);
        return Ok(profile);
    }

    [HttpPut("me")]
    public async Task<ActionResult<ProfileDto>> UpdateMyProfile([FromBody] UpdateProfileCommand command)
    {
        command = command with { UserId = GetCurrentUserId() };
        var profile = await _mediator.Send(command);
        return Ok(profile);
    }

    private Guid GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst("sub")?.Value;
        return Guid.Parse(userIdClaim!);
    }
}
```

### 9. Configuration Startup

#### Api/Program.cs

```csharp
using Microsoft.EntityFrameworkCore;
using Jlc.Infrastructure.Data;
using Jlc.Infrastructure.Repositories;
using Jlc.Application;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Database
builder.Services.AddDbContext<JlcDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Repositories
builder.Services.AddScoped<IProfileRepository, ProfileRepository>();
builder.Services.AddScoped<IValidationRepository, ValidationRepository>();

// MediatR
builder.Services.AddMediatR(cfg => 
    cfg.RegisterServicesFromAssembly(typeof(Application.AssemblyReference).Assembly));

// AutoMapper
builder.Services.AddAutoMapper(typeof(Application.AssemblyReference).Assembly);

// FluentValidation
builder.Services.AddValidatorsFromAssembly(typeof(Application.AssemblyReference).Assembly);

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
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
    });

// CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins("http://localhost:3000", "http://localhost:5173")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

var app = builder.Build();

// Configure pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### 10. appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=jlc_db;Username=postgres;Password=postgres"
  },
  "Jwt": {
    "Issuer": "jlc-auth",
    "Audience": "jlc-api",
    "Key": "your-super-secret-jwt-key-min-32-chars"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

### 11. Script de Migration de Données (MongoDB → PostgreSQL)

#### scripts/migrate_mongo_to_postgres.py

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import asyncpg
import uuid
from datetime import datetime

async def migrate_data():
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient('mongodb://localhost:27017')
    mongo_db = mongo_client['jlc_db']
    
    # Connect to PostgreSQL
    pg_conn = await asyncpg.connect(
        host='localhost',
        database='jlc_db',
        user='postgres',
        password='postgres'
    )
    
    print("🔄 Starting migration from MongoDB to PostgreSQL...")
    
    # Migrate Profiles
    print("\n📄 Migrating profiles...")
    profiles = await mongo_db.profiles.find({}, {'_id': 0}).to_list(length=None)
    
    for profile in profiles:
        # Convert ObjectId strings to UUIDs or keep as is
        profile_id = uuid.UUID(profile['id']) if 'id' in profile else uuid.uuid4()
        user_id = uuid.UUID(profile['user_id'])
        
        await pg_conn.execute("""
            INSERT INTO profiles (id, user_id, profile_type, first_name, last_name, phone, avatar_url, 
                                  agency_data, company_data, interim_data, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb, $10::jsonb, $11, $12)
            ON CONFLICT (id) DO NOTHING
        """, profile_id, user_id, profile['profile_type'], 
            profile.get('first_name'), profile.get('last_name'), profile.get('phone'), profile.get('avatar_url'),
            json.dumps(profile.get('agency_data')), json.dumps(profile.get('company_data')), 
            json.dumps(profile.get('interim_data')),
            datetime.fromisoformat(profile['created_at']), datetime.fromisoformat(profile['updated_at']))
    
    print(f"  ✅ Migrated {len(profiles)} profiles")
    
    # Migrate Validations
    print("\n✅ Migrating validations...")
    validations = await mongo_db.account_validations.find({}, {'_id': 0}).to_list(length=None)
    
    for validation in validations:
        validation_id = uuid.UUID(validation['id'])
        user_id = uuid.UUID(validation['user_id'])
        reviewed_by = uuid.UUID(validation['reviewed_by']) if validation.get('reviewed_by') else None
        
        await pg_conn.execute("""
            INSERT INTO account_validations (id, user_id, user_email, user_name, validation_type, status,
                                             comment, reviewed_by, reviewed_by_email, reviewed_at, 
                                             created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            ON CONFLICT (id) DO NOTHING
        """, validation_id, user_id, validation.get('user_email'), validation.get('user_name'),
            validation['validation_type'], validation['status'], validation.get('comment'),
            reviewed_by, validation.get('reviewed_by_email'), 
            datetime.fromisoformat(validation['reviewed_at']) if validation.get('reviewed_at') else None,
            datetime.fromisoformat(validation['created_at']), datetime.fromisoformat(validation['updated_at']))
    
    print(f"  ✅ Migrated {len(validations)} validations")
    
    # Close connections
    await pg_conn.close()
    mongo_client.close()
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate_data())
```

## 🚀 Lancement de l'Application .NET

```bash
# 1. Démarrer PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# 2. Appliquer les migrations
cd apps/api/src/Jlc.Infrastructure
dotnet ef database update --startup-project ../Jlc.Api/Jlc.Api.csproj

# 3. Lancer l'API
cd ../Jlc.Api
dotnet run

# 4. Accéder à Swagger
# http://localhost:5000/swagger
```

## 📝 Notes Importantes

1. **Tests**: Implémenter des tests unitaires et d'intégration pour chaque layer
2. **Sécurité**: 
   - Valider les JWT avec l'auth-microservice
   - Implémenter RBAC avec policies
   - Ajouter rate limiting
3. **Performance**: 
   - Utiliser AsNoTracking() pour les lectures
   - Implémenter le caching (Redis)
   - Optimiser les requêtes avec Include/ThenInclude
4. **Production**:
   - Utiliser Serilog avec sinks appropriés
   - Configurer Health Checks
   - Implémenter Circuit Breaker (Polly)

## 📦 Livraison

Une fois la migration terminée, vous aurez:
- Un backend .NET 8 avec Clean Architecture
- Une base PostgreSQL avec migrations
- Le frontend React conservé (aucun changement côté API)
- Des tests complets
- Une documentation API (Swagger)

Pour toute question: contact@jlcgroup.com
