using RiskBff.Clients;
using Microsoft.Extensions.Http.Resilience;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();

// Configure OpenAPI/Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure typed HttpClient for the Python Risk Service
var riskServiceUrl = builder.Configuration.GetValue<string>("RiskServiceUrl") ?? "http://localhost:8000";

builder.Services.AddHttpClient<IRiskServiceClient, RiskServiceClient>(client =>
{
    client.BaseAddress = new Uri(riskServiceUrl);
})
.AddStandardResilienceHandler(); // Adds Polly retries, circuit breaker, etc.

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
if (!string.IsNullOrEmpty(connectionString))
{
    builder.Services.AddNpgsqlDataSource(connectionString);
}

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
    app.UseDeveloperExceptionPage();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
