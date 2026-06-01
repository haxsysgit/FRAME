import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { productsService } from '../services/products'

export const useProductsStore = defineStore('products', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Pagination
  const currentPage = ref(1)
  const pageSize = ref(30)
  const hasMore = ref(false)

  const filters = ref({
    name: '',
    therapeutic_category: '',
    product_type: '',
  })

  const filtered = computed(() => {
    if (!filters.value.product_type) return items.value
    return items.value.filter((p) => p.product_type === filters.value.product_type)
  })

  const pageStart = computed(() => (currentPage.value - 1) * pageSize.value + 1)
  const pageEnd = computed(() => pageStart.value + filtered.value.length - 1)

  async function fetchProducts(page = 1) {
    loading.value = true
    error.value = null
    try {
      const params = {
        limit: pageSize.value,
        offset: (page - 1) * pageSize.value,
      }
      if (filters.value.name) params.name = filters.value.name
      if (filters.value.therapeutic_category)
        params.therapeutic_category = filters.value.therapeutic_category
      const result = await productsService.list(params)
      items.value = result
      currentPage.value = page
      hasMore.value = result.length === pageSize.value
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function goToPage(page) {
    if (page < 1) return
    if (page > currentPage.value && !hasMore.value) return
    await fetchProducts(page)
  }

  async function createProduct(payload) {
    const created = await productsService.create(payload)
    await fetchProducts(currentPage.value)
    return created
  }

  async function updateProduct(id, payload) {
    const updated = await productsService.update(id, payload)
    const idx = items.value.findIndex((p) => p.id === id)
    if (idx !== -1) items.value[idx] = updated
    return updated
  }

  async function removeProduct(id) {
    await productsService.remove(id)
    await fetchProducts(currentPage.value)
  }

  return {
    items,
    filtered,
    loading,
    error,
    filters,
    currentPage,
    pageSize,
    hasMore,
    pageStart,
    pageEnd,
    fetchProducts,
    goToPage,
    createProduct,
    updateProduct,
    removeProduct,
  }
})
