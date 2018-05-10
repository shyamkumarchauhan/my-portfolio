import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):

    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:146254080149:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3')

        portfolio_bucket = s3.Bucket('portfolio.crudeoilmcx.com')
        build_bucket = s3.Bucket('portfoliobuild.crudeoilmcx.com')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')


        print "Job Done!"
        topic.publish(Subject="Portfolio Deployed", Message="potfolio deployed successfully")
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="portfolio deployment failed")
        raise
    return 'Hello from Lambda'
