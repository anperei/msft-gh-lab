param name string
param location string = resourceGroup().location
param tags object = {}
param serviceName string = ''
param containerAppsEnvironmentName string
param containerRegistryName string
param containerName string
param containerImage string
param targetPort int = 80
param env array = []
param minReplicas int = 0
param maxReplicas int = 10
param enableProbes bool = false
param enableManagedIdentity bool = false  // Enable system-assigned managed identity
param external bool = true  // Whether the container app is externally accessible
param allowInsecure bool = false  // Allow HTTP traffic for internal container-to-container communication

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: containerAppsEnvironmentName
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: containerRegistryName
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  tags: union(tags, !empty(serviceName) ? { 'azd-service-name': serviceName } : {})
  identity: enableManagedIdentity ? {
    type: 'SystemAssigned'
  } : {
    type: 'None'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: external
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: allowInsecure
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'registry-password'
        }
      ]
      secrets: [
        {
          name: 'registry-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerName
          image: containerImage
          env: env
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: enableProbes ? [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: targetPort
              }
              initialDelaySeconds: 10
              periodSeconds: 10
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: targetPort
              }
              initialDelaySeconds: 5
              periodSeconds: 5
            }
            {
              type: 'Startup'
              httpGet: {
                path: '/health'
                port: targetPort
              }
              initialDelaySeconds: 0
              periodSeconds: 5
              failureThreshold: 30
            }
          ] : []
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
}

output name string = containerApp.name
output uri string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output id string = containerApp.id
output identityPrincipalId string = enableManagedIdentity ? containerApp.identity.principalId : ''
