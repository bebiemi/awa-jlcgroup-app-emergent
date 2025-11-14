/**
 * ESLint Rule: no-invalid-api-endpoints
 * 
 * Détecte et empêche :
 * - Les duplications /api/api/...
 * - Les endpoints sans préfixe /api
 * - Les createBaseQueryWithAuth() avec paramètres
 */

module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce valid API endpoint patterns',
      category: 'Best Practices',
      recommended: true,
    },
    fixable: 'code',
    schema: [],
    messages: {
      duplicateApi: 'Duplicate /api/ detected in endpoint: {{endpoint}}',
      missingApiPrefix: 'Endpoint must start with /api/: {{endpoint}}',
      baseQueryWithParam: 'createBaseQueryWithAuth() should not receive parameters. Use default /api baseUrl.',
    },
  },

  create(context) {
    return {
      // Détecter les chaînes de caractères contenant des endpoints
      Literal(node) {
        if (typeof node.value !== 'string') return

        const value = node.value

        // Vérifier la duplication /api/api/
        if (value.includes('/api/api/')) {
          context.report({
            node,
            messageId: 'duplicateApi',
            data: { endpoint: value },
          })
        }

        // Vérifier les endpoints qui ressemblent à des chemins API sans /api
        const apiLikePattern = /^\/(auth|iam|users|profiles|security|emails|missions|contracts)\//
        if (apiLikePattern.test(value) && !value.startsWith('/api/')) {
          // Exception pour les routes de navigation
          const parent = context.getAncestors().slice(-1)[0]
          const isRouteConfig = parent && parent.type === 'JSXAttribute' && parent.name.name === 'path'
          
          if (!isRouteConfig) {
            context.report({
              node,
              messageId: 'missingApiPrefix',
              data: { endpoint: value },
              fix(fixer) {
                return fixer.replaceText(node, `"/api${value}"`)
              },
            })
          }
        }
      },

      // Détecter createBaseQueryWithAuth avec paramètres
      CallExpression(node) {
        if (
          node.callee.type === 'Identifier' &&
          node.callee.name === 'createBaseQueryWithAuth' &&
          node.arguments.length > 0
        ) {
          // Accepter seulement undefined ou rien
          const firstArg = node.arguments[0]
          if (firstArg.type !== 'Identifier' || firstArg.name !== 'undefined') {
            context.report({
              node,
              messageId: 'baseQueryWithParam',
              fix(fixer) {
                return fixer.replaceText(node, 'createBaseQueryWithAuth()')
              },
            })
          }
        }
      },
    }
  },
}
