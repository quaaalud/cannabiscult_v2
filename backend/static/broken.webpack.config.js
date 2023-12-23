const path = require('path');
const glob = require('glob');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const webpack = require('webpack');

function getAllFilesFromDir(dir, fileTypes) {
  const pattern = `${dir}/**/*.+(${fileTypes.join('|')})`;
  return glob.sync(pattern);
}

module.exports = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  entry: () => {
    const fileTypes = ['js', 'css', 'scss'];
    const allFiles = getAllFilesFromDir('./', fileTypes);
    const entry = {};

    allFiles.forEach(file => {
      const relativePath = path.relative('./', file);
      const entryName = relativePath.replace(path.extname(relativePath), '');
      entry[entryName] = './' + file;
    });

    return entry;
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].bundle.js'
  },
  optimization: {
    innerGraph: true,
    flagIncludedChunks: true,
    concatenateModules: true,
    minimize: true,
    minimizer: [
      new TerserPlugin({ test: /\.js(\?.*)?$/i }),
      new CssMinimizerPlugin()
    ],
    splitChunks: { chunks: 'all' },
    runtimeChunk: 'single'
  },
  plugins: [
    new webpack.ProvidePlugin({ Chart: 'chart.js' }),
    new MiniCssExtractPlugin({ filename: '[name].[contenthash].css' })
  ],
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: { presets: ['@babel/preset-env'] }
        }
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx', '.json', '.css', '.scss'],
  },
  devtool: process.env.NODE_ENV === 'development' ? 'source-map' : false
};
