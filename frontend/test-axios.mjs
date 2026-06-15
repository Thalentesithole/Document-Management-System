import axios from 'axios'

async function test() {
  const api = axios.create({
    baseURL: 'http://localhost:5174/api/v1',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  try {
    const formData = new URLSearchParams()
    formData.append('username', 'testnew@example.com')
    formData.append('password', 'wrong')

    await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  } catch (err) {
    console.log("Error status:", err.response?.status)
    console.log("Error data:", err.response?.data)
    console.log("Is detail an array?", Array.isArray(err.response?.data?.detail))
    console.log("Detail string:", err.response?.data?.detail)
  }
}

test()
