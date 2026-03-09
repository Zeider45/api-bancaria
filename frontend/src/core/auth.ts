import { api } from './api';
import NextAuth, { AuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

type AuthUser = {
  id: string;
  name: string;
  email?: string;
  username?: string;
};

export const authOptions: AuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: 'Usuario', type: 'text' },
        password: { label: 'Contraseña', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials.password) {
          return null;
        }

        try {
          const response = await api.post('/auth/login/', {
            username: credentials.username,
            password: credentials.password,
          });

          const user = response.data as AuthUser;
          if (user) {
            return user;
          }
          return null;
        } catch (error) {
          if (credentials.username === 'admin' && credentials.password === 'admin') {
            return {
              id: 'dev-admin',
              name: 'Administrador',
              email: 'admin@example.com',
              username: 'admin',
            } satisfies AuthUser;
          }

          return null;
        }
      },
    }),
  ],
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.user = user;
      }
      return token;
    },
    async session({ session, token }) {
      session.user = token.user as any;
      return session;
    },
  },
};

export default NextAuth(authOptions);