const EMOJI_MAP = [
  { keywords: ['cattle', 'cow', 'bull', 'bovine', 'dairy'], emoji: '🐄' },
  { keywords: ['sheep', 'lamb', 'ewe', 'ram'],              emoji: '🐑' },
  { keywords: ['goat', 'kid', 'doe', 'buck'],               emoji: '🐐' },
  { keywords: ['pig', 'swine', 'hog', 'boar', 'sow'],      emoji: '🐷' },
  { keywords: ['chicken', 'poultry', 'hen', 'rooster', 'chick', 'layer', 'broiler'], emoji: '🐔' },
  { keywords: ['horse', 'mare', 'stallion', 'foal', 'pony'], emoji: '🐎' },
  { keywords: ['rabbit', 'bunny'],                           emoji: '🐇' },
  { keywords: ['duck', 'drake'],                             emoji: '🦆' },
  { keywords: ['turkey'],                                    emoji: '🦃' },
  { keywords: ['donkey', 'ass', 'mule'],                    emoji: '🫏' },
]

export function getAnimalEmoji(livestockTypeName = '') {
  const lower = livestockTypeName.toLowerCase()
  const match = EMOJI_MAP.find(e => e.keywords.some(k => lower.includes(k)))
  return match?.emoji ?? '🐾'
}

export function getAnimalEmojiById(livestockTypes = [], typeId) {
  const lt = livestockTypes.find(t => t.id === typeId)
  return getAnimalEmoji(lt?.name ?? '')
}
