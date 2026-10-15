
using System.Net.Http.Json;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddHttpClient("AiService", client =>
{
    client.BaseAddress = new Uri(
        builder.Configuration["AiService:BaseUrl"]
        ?? "http://localhost:8000");

    client.Timeout = TimeSpan.FromSeconds(60);
});

var app = builder.Build();

app.MapGet("/health", () =>
    Results.Ok(new { Status = "Healthy" }));

app.MapPost("/api/ai/rag", async (
    AiRequest request,
    IHttpClientFactory factory,
    CancellationToken cancellationToken) =>
{
    if (string.IsNullOrWhiteSpace(request.Question)
        || request.Question.Length > 4000)
    {
        return Results.BadRequest(
            "A valid question is required.");
    }

    var client = factory.CreateClient("AiService");

    using var response = await client.PostAsJsonAsync(
        "/ai/rag",
        request,
        cancellationToken);

    var body = await response.Content.ReadAsStringAsync(
        cancellationToken);

    return Results.Content(
        body,
        "application/json",
        statusCode: (int)response.StatusCode);
});

app.MapPost("/api/ai/investigate", async (
    AiRequest request,
    IHttpClientFactory factory,
    CancellationToken cancellationToken) =>
{
    if (string.IsNullOrWhiteSpace(request.Question)
        || request.Question.Length > 4000)
    {
        return Results.BadRequest(
            "A valid question is required.");
    }

    var client = factory.CreateClient("AiService");

    using var response = await client.PostAsJsonAsync(
        "/ai/investigate",
        request,
        cancellationToken);

    var body = await response.Content.ReadAsStringAsync(
        cancellationToken);

    return Results.Content(
        body,
        "application/json",
        statusCode: (int)response.StatusCode);
});

app.Run();

public record AiRequest(string Question);
