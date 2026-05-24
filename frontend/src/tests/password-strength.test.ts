import { describe, it, expect } from 'vitest';

function passwordStrength(pw: string): number {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;
  return score;
}

describe('passwordStrength', () => {
  it('should return 0 for empty string', () => {
    expect(passwordStrength('')).toBe(0);
  });

  it('should return 2 for short password with mixed case + digit', () => {
    expect(passwordStrength('Abc1')).toBe(2);
  });

  it('should return 2 for 8+ chars with mixed case', () => {
    expect(passwordStrength('Abcdefgh')).toBe(2);
  });

  it('should return 2 for 8+ chars with number', () => {
    expect(passwordStrength('abcdefgh1')).toBe(2);
  });

  it('should return 3 for 8+ chars + mixed case + number', () => {
    expect(passwordStrength('Abcdefgh1')).toBe(3);
  });

  it('should return 4 for full criteria', () => {
    expect(passwordStrength('Abcdefgh1!')).toBe(4);
  });

  it('should return 3 for 8+ chars + mixed case + special', () => {
    expect(passwordStrength('Abcdefgh!')).toBe(3);
  });

  it('should return 3 for 8+ chars + number + special (no mixed case)', () => {
    expect(passwordStrength('abcdefgh1!')).toBe(3);
  });

  it('should handle very long passwords', () => {
    expect(passwordStrength('A' + 'a'.repeat(50) + '1!')).toBe(4);
  });

  it('should handle only lowercase', () => {
    expect(passwordStrength('abcdefgh')).toBe(1);
  });

  it('should handle only uppercase', () => {
    expect(passwordStrength('ABCDEFGH')).toBe(1);
  });

  it('should handle only numbers (length + digit)', () => {
    expect(passwordStrength('12345678')).toBe(2);
  });
});
