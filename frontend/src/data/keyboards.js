/**
 * Special character maps for African language keyboards.
 * Used by SpecialCharKeyboard.vue.
 */
export const KEYBOARDS = {
  yo: {
    label: 'Yoruba',
    chars: ['ẹ', 'Ẹ', 'ọ', 'Ọ', 'ṣ', 'Ṣ', 'à', 'á', 'è', 'é', 'ì', 'í', 'ò', 'ó', 'ù', 'ú', 'ǹ', 'ń'],
  },
  am: {
    label: 'Amharic',
    chars: [], // Ge'ez script — defer to system keyboard
    note: 'Amharic uses Ge'ez script. Switch to Amharic keyboard on your device for best results.',
  },
  zu: {
    label: 'Zulu',
    chars: ['á', 'é', 'í', 'ó', 'ú', 'ā', 'ē', 'ī', 'ō', 'ū'],
    note: 'Zulu uses standard Latin letters. Click consonants (c, q, x) are standard keys.',
  },
  sw: {
    label: 'Swahili',
    chars: [], // Standard Latin — no special chars needed
    note: 'Swahili uses standard Latin script. No special characters required.',
  },
}
