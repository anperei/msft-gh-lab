targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Whether to enable Cosmos DB Free Tier (only one per subscription)')
param cosmosFreeTierEnabled bool = false

// Tags that should be applied to all resources
var tags = {
  'azd-env-name': environmentName
}

// Generate a unique token for resource naming
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Computed resource names
var cosmosAccountName = 'cosmos-${resourceToken}'
var cosmosDatabaseName = 'inventory'
var cosmosDevicesContainerName = 'devices'

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

// Container Apps Environment
module containerAppsEnvironment 'core/host/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: 'cae-${resourceToken}'
    location: location
    tags: tags
  }
}

// Container Registry
module containerRegistry 'core/host/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: 'cr${resourceToken}'
    location: location
    tags: tags
  }
}

// Cosmos DB account, database, and containers
module cosmos 'core/data/cosmos.bicep' = {
  name: 'cosmos'
  scope: rg
  params: {
    accountName: cosmosAccountName
    location: location
    tags: tags
    enableFreeTier: cosmosFreeTierEnabled
    databaseName: cosmosDatabaseName
    devicesContainerName: cosmosDevicesContainerName
    enableServerless: true
  }
}

// Backend Container App (uses system-assigned managed identity for Cosmos DB access)
module backend 'core/host/container-app.bicep' = {
  name: 'backend'
  scope: rg
  params: {
    name: 'ca-backend-${resourceToken}'
    location: location
    tags: tags
    serviceName: 'backend'
    containerAppsEnvironmentName: containerAppsEnvironment.outputs.name
    containerRegistryName: containerRegistry.outputs.name
    containerName: 'backend'
    containerImage: 'nginx:latest' // Placeholder, will be replaced by azd
    targetPort: 8000
    minReplicas: 1
    enableProbes: false  // Disable probes to prevent timeout during provisioning
    enableManagedIdentity: true  // Use system-assigned managed identity
    external: false  // Internal: only accessible within Container Apps Environment
    allowInsecure: true  // Allow HTTP for internal container-to-container communication
    env: [
      {
        name: 'COSMOS_ENDPOINT'
        value: cosmos.outputs.endpoint
      }
      {
        name: 'COSMOS_DB_NAME'
        value: cosmosDatabaseName
      }
      {
        name: 'COSMOS_DEVICES_CONTAINER'
        value: cosmosDevicesContainerName
      }
    ]
  }
}

// Cosmos DB RBAC role assignment for backend managed identity
// This must be deployed after both cosmos and backend to get the principal ID
module cosmosRbac 'core/data/cosmos-rbac.bicep' = {
  name: 'cosmos-rbac'
  scope: rg
  params: {
    accountName: cosmosAccountName
    principalId: backend.outputs.identityPrincipalId
  }
}

// Frontend Container App
module frontend 'core/host/container-app.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    name: 'ca-frontend-${resourceToken}'
    location: location
    tags: tags
    serviceName: 'frontend'
    containerAppsEnvironmentName: containerAppsEnvironment.outputs.name
    containerRegistryName: containerRegistry.outputs.name
    containerName: 'frontend'
    containerImage: 'nginx:latest' // Placeholder, will be replaced by azd
    targetPort: 80
    minReplicas: 0
    env: [
      {
        name: 'BACKEND_URL'
        value: 'http://${backend.outputs.name}.internal.${containerAppsEnvironment.outputs.defaultDomain}'  // Internal DNS name for container-to-container communication
      }
    ]
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name
output BACKEND_URI string = backend.outputs.uri
output FRONTEND_URI string = frontend.outputs.uri
output COSMOS_ENDPOINT string = cosmos.outputs.endpoint
output COSMOS_DB_NAME string = cosmosDatabaseName
