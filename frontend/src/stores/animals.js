import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listAnimals } from '@/api/animals'
import { listLivestockTypes } from '@/api/livestock'

export const useAnimalStore = defineStore('animals', () => {
  const animals = ref([])
  const livestockTypes = ref([])

  async function fetchAnimals(params) {
    animals.value = await listAnimals(params)
  }

  async function fetchLivestockTypes() {
    livestockTypes.value = await listLivestockTypes()
  }

  return { animals, livestockTypes, fetchAnimals, fetchLivestockTypes }
})
