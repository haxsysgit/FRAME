import { ref } from 'vue'

const confirmState = ref({
  visible: false,
  title: '',
  message: '',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  confirmStyle: 'danger',
  resolve: null,
})

export function useConfirm() {
  const confirm = ({ title = 'Confirm', message, confirmText = 'Confirm', cancelText = 'Cancel', confirmStyle = 'danger' } = {}) => {
    return new Promise((resolve) => {
      confirmState.value = {
        visible: true,
        title,
        message,
        confirmText,
        cancelText,
        confirmStyle,
        resolve,
      }
    })
  }

  const handleConfirm = () => {
    if (confirmState.value.resolve) {
      confirmState.value.resolve(true)
    }
    confirmState.value.visible = false
  }

  const handleCancel = () => {
    if (confirmState.value.resolve) {
      confirmState.value.resolve(false)
    }
    confirmState.value.visible = false
  }

  return {
    confirmState,
    confirm,
    handleConfirm,
    handleCancel,
  }
}
