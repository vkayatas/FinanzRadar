// Format date helper - 2025-09-29T14:30:00Z to  29.9.2025, 16:30:00
export const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleString()
}