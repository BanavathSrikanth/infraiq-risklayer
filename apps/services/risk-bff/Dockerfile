FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy csproj and restore as distinct layers
COPY ["RiskBff.csproj", "./"]
RUN dotnet restore "RiskBff.csproj"

# Copy everything else and build
COPY . .
RUN dotnet publish "RiskBff.csproj" -c Release -o /app/publish

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "RiskBff.dll"]
