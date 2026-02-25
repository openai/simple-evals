const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const Css = require('mini-css-extract-plugin');
const FavIconsWebpackPlugin = require('favicons-webpack-plugin');

module.exports = {
  entry: {
    main: './examples/src/index.tsx',
  },
  mode: process.env.NODE_ENV === 'production' ?
    'production' : 'development',
  resolve: {
    extensions: ['.jsx', '.tsx', '.ts', '.scss', '.css', '.js'],
  },
  output: {
    path: path.resolve(__dirname, 'examples/dist'),
    filename: '[name].js',
  },
  devServer: {
    contentBase: path.resolve(__dirname, 'examples/dist'),
    port: 8000,
    hot: true,
  },
  module: {
    rules: [{
        test: /\.tsx?$/,
        use: [{
          loader: 'ts-loader',
          options: {
            configFile: 'tsconfig.examples.json',
          },
        }],
        exclude: /node_modules/,
      },
      {
        test: /\.s?css$/,
        use: [
          Css.loader,
          'css-loader',
          'sass-loader',
        ],
      },
      {
        test: /\.xml|.rjs|.java/,
        use: 'raw-loader',
      },
      {
        test: /\.svg|.png/,
        use: 'file-loader',
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './examples/src/index.ejs',
    }),
    new FavIconsWebpackPlugin('./logo-standalone.png'),
    new Css({
      filename: 'main.css',
    }),
  ],
};
