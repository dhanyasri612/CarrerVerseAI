import api from './api'

export const listResumes = async () => {
  const response = await api.get('/resume')
  return response.data
}

export const uploadResume = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const parseResume = async (resumeId) => {
  const response = await api.post(`/parser/resume/${resumeId}`)
  return response.data
}
