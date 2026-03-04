import { create } from "zustand"
import { format } from "date-fns"

interface UIState {
  isBlockModalOpen: boolean
  editingBlockId: string | null
  selectedDate: string  // "YYYY-MM-DD"

  openCreateModal: () => void
  openEditModal: (blockId: string) => void
  closeBlockModal: () => void
  setSelectedDate: (date: string) => void
}

export const useUIStore = create<UIState>((set) => ({
  isBlockModalOpen: false,
  editingBlockId: null,
  selectedDate: format(new Date(), "yyyy-MM-dd"),

  openCreateModal: () => set({ isBlockModalOpen: true, editingBlockId: null }),
  openEditModal: (blockId) => set({ isBlockModalOpen: true, editingBlockId: blockId }),
  closeBlockModal: () => set({ isBlockModalOpen: false, editingBlockId: null }),
  setSelectedDate: (date) => set({ selectedDate: date }),
}))
