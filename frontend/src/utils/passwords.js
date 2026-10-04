export function passwordRequirements(value) {
  return [
    { label: 'At least 9 characters', met: [...value].length >= 9 },
    { label: 'An uppercase letter (A-Z)', met: /[A-Z]/.test(value) },
    { label: 'A lowercase letter (a-z)', met: /[a-z]/.test(value) },
    { label: 'A digit (0-9)', met: /[0-9]/.test(value) },
    { label: 'A special character, such as ! @ # _', met: /[!"#$%&'()*+,\-./:;<=>?@[\]\\^_`{|}~]/.test(value) },
    { label: 'At most 72 UTF-8 bytes; no null characters', met: new TextEncoder().encode(value).length <= 72 && !value.includes('\0') },
  ]
}

export const validNewPassword = value => passwordRequirements(value).every(item => item.met)
